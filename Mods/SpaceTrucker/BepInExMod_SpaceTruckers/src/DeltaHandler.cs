using HarmonyLib;
using Ostranauts.Core;

namespace NeonDistraction.SpaceTruckers.Delta
{
  [HarmonyPatch(typeof(DataHandler), nameof(DataHandler.LoadMod))]
  internal static class FindModDataFolders
  {
    [HarmonyPrefix]
    private static void ReportModDataFolders(string strFolderPath, string[] aIgnorePatterns, JsonModInfo jmi)
    {
      ModLoadReporter.Report(strFolderPath, aIgnorePatterns, jmi);
      DeltaDocumentStore.Collect(strFolderPath);
    }
  }

  [HarmonyPatch(typeof(System.IO.File), nameof(System.IO.File.ReadAllText), new[] { typeof(string) })]
  internal static class DeltaFileReadPatch
  {
    [HarmonyPrefix]
    private static bool ApplyDeltaBeforeRead(string path, ref string __result)
    {
      if (!DeltaDocumentStore.TryApply(path, out string patchedJson))
        return true;

      __result = patchedJson;
      return false;
    }
  }
}
