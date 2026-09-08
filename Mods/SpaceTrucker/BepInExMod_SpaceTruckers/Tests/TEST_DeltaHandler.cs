using Microsoft.VisualStudio.TestTools.UnitTesting;
using NeonDistraction.SpaceTruckers.Delta;
using Newtonsoft.Json.Linq;
using System;
using System.IO;

namespace NeonDistraction.SpaceTruckers.Tests
{
  [TestClass]
  public class TEST_DeltaHandler
  {
    [TestMethod]
    public void TryApply_AppliesCondOwnerDelta_AndMatchesExpectedFixture()
    {
      string testRoot = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString("N"));

      try
      {
        DeltaDocumentStore.Collect(testRoot);
        string sourceFile = Path.Combine(testRoot, "Original_condowners.json");
        Assert.IsTrue(DeltaDocumentStore.TryApply(sourceFile, out string patchedJson));

        JToken expected = JToken.Parse(File.ReadAllText(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "TestAgainst_condowners.json")));
        JToken actual = JToken.Parse(patchedJson);
        Assert.IsTrue(JToken.DeepEquals(expected, actual), "Patched condowners JSON does not match TestAgainst_condowners.json.");
      }
      finally
      {
        if (Directory.Exists(testRoot))
          Directory.Delete(testRoot, true);
      }
    }
  }
}
