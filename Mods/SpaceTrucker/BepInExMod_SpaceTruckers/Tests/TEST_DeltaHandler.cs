using Microsoft.VisualStudio.TestTools.UnitTesting;
using NeonDistraction.SpaceTruckers.Delta;
using Newtonsoft.Json.Linq;
using System;
using System.IO;

namespace NeonDistraction.SpaceTruckers.Tests
{
  // D:\Projects\Ostranauts\Github\NeonDistraction_Ostranauts\Mods\SpaceTrucker\BepInExMod_SpaceTruckers\Tests\data\
  [TestClass]
  public class TEST_DeltaHandler
  {
    [TestMethod]
    public void TryApply_AppliesCondOwnerDelta_AndMatchesExpectedFixture()
    {
      string testRoot = Path.GetDirectoryName(typeof(TEST_DeltaHandler).Assembly.Location)!;
      string testDataPath = Path.Combine(testRoot, "data");
      string sourceFile = Path.Combine(testDataPath, "condowners", "condowners.json");
      string originalJson = File.ReadAllText(sourceFile);

      DeltaDocumentStore.Collect(testRoot);

      Assert.IsTrue(DeltaDocumentStore.TryApply(sourceFile, out string patchedJson), DeltaDocumentStore.LastError);
      Assert.AreEqual(originalJson, File.ReadAllText(sourceFile), "Delta handling must not write to the source JSON file.");

      JToken expected = JToken.Parse(File.ReadAllText(Path.Combine(testRoot, "TestAgainst_condowners.json")));
      JToken actual = JToken.Parse(patchedJson);
      
      // For diagnostics write the patched JSON to a file in the test data folder.
      string patchedFile = Path.Combine(@"D:\Projects\Ostranauts\Github\NeonDistraction_Ostranauts\Mods\SpaceTrucker\BepInExMod_SpaceTruckers\Tests\", "DIAGNOSTIC_condowners_patched.json");
      File.WriteAllText(patchedFile, patchedJson);
      
      Assert.IsTrue(JToken.DeepEquals(expected, actual), "Patched condowners JSON does not match TestAgainst_condowners.json.");

    }
  }
}
