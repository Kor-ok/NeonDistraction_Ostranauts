using Marvin.JsonPatch;
using Marvin.JsonPatch.Operations;
using Newtonsoft.Json.Linq;
using System;
using System.Globalization;

namespace NeonDistraction.SpaceTruckers.Delta
{
  internal static class JsonPatchExecutor
  {
    internal static void Apply(JsonPatchDocument<object> document, JObject target)
    {
      foreach (Operation<object> operation in document.Operations)
        Apply(operation, target);
    }

    private static void Apply(Operation<object> operation, JObject target)
    {
      switch (operation.op)
      {
        case "add":
          Add(target, operation.path, ToToken(operation.value));
          break;
        case "remove":
          Remove(target, operation.path);
          break;
        case "replace":
          Replace(target, operation.path, ToToken(operation.value));
          break;
        case "copy":
          Add(target, operation.path, Get(target, operation.from).DeepClone());
          break;
        case "move":
          JToken moved = Get(target, operation.from).DeepClone();
          Remove(target, operation.from);
          Add(target, operation.path, moved);
          break;
        case "test":
          if (!JToken.DeepEquals(Get(target, operation.path), ToToken(operation.value)))
            throw new InvalidOperationException($"JSON Patch test failed at {operation.path}.");
          break;
        default:
          throw new NotSupportedException($"Unsupported JSON Patch operation '{operation.op}'.");
      }
    }

    private static JToken ToToken(object value) => value as JToken ?? JToken.FromObject(value);

    private static JToken Get(JObject target, string path)
    {
      JToken current = target;
      foreach (string segment in Segments(path))
      {
        if (current is JObject obj && obj[segment] is JToken property)
          current = property;
        else if (current is JArray array && int.TryParse(segment, NumberStyles.None, CultureInfo.InvariantCulture, out int index) && index >= 0 && index < array.Count)
          current = array[index];
        else
          throw new InvalidOperationException($"JSON Pointer path '{path}' does not exist.");
      }
      return current;
    }

    private static void Add(JObject target, string path, JToken value)
    {
      JToken parent = GetParent(target, path, out string segment);
      if (parent is JObject obj)
        obj[segment] = value;
      else if (parent is JArray array)
      {
        if (segment == "-")
          array.Add(value);
        else if (int.TryParse(segment, NumberStyles.None, CultureInfo.InvariantCulture, out int index) && index >= 0 && index <= array.Count)
          array.Insert(index, value);
        else
          throw new InvalidOperationException($"JSON Pointer array index '{segment}' is invalid.");
      }
      else
        throw new InvalidOperationException($"JSON Pointer path '{path}' has no object or array parent.");
    }

    private static void Replace(JObject target, string path, JToken value)
    {
      JToken parent = GetParent(target, path, out string segment);
      if (parent is JObject obj && obj[segment] != null)
        obj[segment] = value;
      else if (parent is JArray array && int.TryParse(segment, NumberStyles.None, CultureInfo.InvariantCulture, out int index) && index >= 0 && index < array.Count)
        array[index] = value;
      else
        throw new InvalidOperationException($"JSON Pointer path '{path}' does not exist.");
    }

    private static void Remove(JObject target, string path)
    {
      JToken token = Get(target, path);
      token.Remove();
    }

    private static JToken GetParent(JObject target, string path, out string segment)
    {
      string[] segments = Segments(path);
      if (segments.Length == 0)
        throw new InvalidOperationException("The document root cannot be modified.");
      segment = segments[segments.Length - 1];
      JToken current = target;
      for (int index = 0; index < segments.Length - 1; index++)
      {
        string currentSegment = segments[index];
        if (current is JObject obj && obj[currentSegment] is JToken property)
          current = property;
        else if (current is JArray array && int.TryParse(currentSegment, NumberStyles.None, CultureInfo.InvariantCulture, out int arrayIndex) && arrayIndex >= 0 && arrayIndex < array.Count)
          current = array[arrayIndex];
        else
          throw new InvalidOperationException($"JSON Pointer path '{path}' does not exist.");
      }
      return current;
    }

    private static string[] Segments(string path)
    {
      if (string.IsNullOrEmpty(path))
        return Array.Empty<string>();
      if (!path.StartsWith("/", StringComparison.Ordinal))
        throw new InvalidOperationException($"JSON Pointer path '{path}' must begin with '/'.");
      string[] segments = path.Substring(1).Split('/');
      for (int index = 0; index < segments.Length; index++)
        segments[index] = segments[index].Replace("~1", "/").Replace("~0", "~");
      return segments;
    }
  }
}
