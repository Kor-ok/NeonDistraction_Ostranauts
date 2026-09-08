using Ostranauts.Core;
using System;
using System.Collections.Generic;
using System.IO;

namespace NeonDistraction.SpaceTruckers.Delta
{
  internal static class ModLoadReporter
  {
    private const string HighlightFolder = "delta";

    internal static void Report(string folderPath, string[] ignorePatterns, JsonModInfo modInfo)
    {
      bool isHighlighted = folderPath.IndexOf(HighlightFolder, StringComparison.OrdinalIgnoreCase) >= 0;
      string highlight = isHighlighted ? " [HIGHLIGHTED]" : string.Empty;
      string formattedIgnorePatterns = ignorePatterns == null || ignorePatterns.Length == 0 ? "<none>" : string.Join(", ", ignorePatterns);
      string formattedTags = modInfo?.aTags == null || modInfo.aTags.Length == 0 ? "<none>" : string.Join(", ", modInfo.aTags);

      Plugin.Log.LogInfo(
        $"[SPACETRUCKERS]{highlight} DataHandler.LoadMod arguments:\n" +
        $"  Folder: {folderPath}\n" +
        $"  Ignore patterns: {formattedIgnorePatterns}\n" +
        $"  Mod name: {modInfo?.strName ?? "<null>"}\n" +
        $"  Author: {modInfo?.strAuthor ?? "<null>"}\n" +
        $"  Mod version: {modInfo?.strModVersion ?? "<null>"}\n" +
        $"  Game version: {modInfo?.strGameVersion ?? "<null>"}\n" +
        $"  Workshop ID: {modInfo?.strWorkshopID ?? "<null>"}\n" +
        $"  Tags: {formattedTags}\n" +
        $"  URL: {modInfo?.strModURL ?? "<null>"}");

      ReportDataFolders(folderPath);
    }

    private static void ReportDataFolders(string modFolderPath)
    {
      string dataFolderPath = Path.Combine(modFolderPath, "data");
      if (!Directory.Exists(dataFolderPath))
      {
        Plugin.Log.LogInfo($"[SPACETRUCKERS] Data folder does not exist: {dataFolderPath}");
        return;
      }

      foreach (string folderPath in Directory.EnumerateDirectories(dataFolderPath, "*", SearchOption.AllDirectories))
      {
        bool isHighlighted = folderPath.IndexOf(HighlightFolder, StringComparison.OrdinalIgnoreCase) >= 0;
        string highlight = isHighlighted ? " [HIGHLIGHTED]" : string.Empty;
        Plugin.Log.LogInfo($"[SPACETRUCKERS]{highlight} Data folder: {folderPath}");
      }
    }
  }
}
