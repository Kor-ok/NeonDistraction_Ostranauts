using BepInEx;
using Marvin.JsonPatch;
using Marvin.JsonPatch.Exceptions;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;

namespace NeonDistraction.SpaceTruckers.Delta
{
  internal static class DeltaDocumentStore
  {
    private const string DeltaFolderName = "delta";

    private static readonly Dictionary<string, Dictionary<string, JArray>> DeltaMap = new Dictionary<string, Dictionary<string, JArray>>(StringComparer.OrdinalIgnoreCase);
    internal static string? LastError { get; private set; }

    internal static void Collect(string modFolderPath)
    {
      string deltaFolderPath = Path.Combine(modFolderPath, "data", DeltaFolderName);
      Trace.WriteLine($"[SPACETRUCKERS] Reading delta JSON from {deltaFolderPath}...");
      if (!Directory.Exists(deltaFolderPath))
        return;

      foreach (string filePath in Directory.EnumerateFiles(deltaFolderPath, "*.json", SearchOption.AllDirectories))
      {
        try
        {
          JObject deltaDocument = JObject.Parse(ReadFileText(filePath));
          if (deltaDocument["targets"] is not JObject deltaTargets)
            continue;

          Dictionary<string, JArray> targets = GetOrCreateTargets(Path.GetFileNameWithoutExtension(filePath));
          foreach (JProperty target in deltaTargets.Properties())
          {
            if (target.Value is not JArray operations)
              continue;

            if (!targets.TryGetValue(target.Name, out JArray? existingOperations))
            {
              existingOperations = new JArray();
              targets.Add(target.Name, existingOperations);
            }

            existingOperations.Merge(operations);
          }
        }
        catch (Exception ex)
        {
          Trace.WriteLine($"[SPACETRUCKERS] Could not read delta JSON from {filePath}: {ex.Message}");
        }
      }
    }

    internal static bool TryApply(string sourceFilePath, out string patchedJson)
    {
      LastError = null;
      patchedJson = string.Empty;
      string dataFolderName = new DirectoryInfo(Path.GetDirectoryName(sourceFilePath) ?? string.Empty).Name;
      if (!DeltaMap.TryGetValue(dataFolderName, out Dictionary<string, JArray>? targets))
        return false;

      try
      {
        JArray sourceEntries = JArray.Parse(ReadFileText(sourceFilePath));
        bool wasPatched = false;
        foreach (JObject entry in sourceEntries.OfType<JObject>())
        {
          string? entryName = entry.Value<string>("strName");
          if (entryName == null || !targets.TryGetValue(entryName, out JArray? operations))
            continue;

          JsonPatchDocument<object>? patch = JsonConvert.DeserializeObject<JsonPatchDocument<object>>(operations.ToString());
          if (patch == null)
            continue;

          JsonPatchExecutor.Apply(patch, entry);
          wasPatched = true;
          Trace.WriteLine($"[SPACETRUCKERS] Applied delta to {dataFolderName}/{entryName} from {sourceFilePath}.");
        }

        if (!wasPatched)
          return false;

        patchedJson = sourceEntries.ToString();
        return true;
      }
      catch (JsonPatchException ex)
      {
        LastError = ex.ToString();
        Trace.WriteLine($"[SPACETRUCKERS] Delta patch failed for {sourceFilePath}: {ex.Message}");
        return false;
      }
      catch (Exception ex)
      {
        LastError = ex.ToString();
        Trace.WriteLine($"[SPACETRUCKERS] Could not apply delta to {sourceFilePath}: {ex.Message}");
        return false;
      }
    }

    private static Dictionary<string, JArray> GetOrCreateTargets(string dataFolderName)
    {
      if (DeltaMap.TryGetValue(dataFolderName, out Dictionary<string, JArray>? targets))
        return targets;

      targets = new Dictionary<string, JArray>(StringComparer.Ordinal);
      DeltaMap.Add(dataFolderName, targets);
      return targets;
    }

    private static string ReadFileText(string filePath)
    {
      using StreamReader reader = new StreamReader(filePath);
      return reader.ReadToEnd();
    }
  }
}
