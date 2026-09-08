using BepInEx;
using BepInEx.Logging;
using BepInEx.Configuration;
using HarmonyLib;
using NeonDistraction.SpaceTruckers.Graphical;

namespace NeonDistraction.SpaceTruckers;

[BepInPlugin(LCMPluginInfo.PLUGIN_GUID, LCMPluginInfo.PLUGIN_NAME, LCMPluginInfo.PLUGIN_VERSION)]
public class Plugin : BaseUnityPlugin
{
  private const string DataHarmonyId = LCMPluginInfo.PLUGIN_GUID + ".data";

  internal static ManualLogSource Log = null!;

  internal static ConfigEntry<bool> configDebugGeneral = null!;

  private void Awake()
  {
    Log = Logger;

    Log.LogInfo("[SPACETRUCKERS] Earliest BepInEx plugin intervention point reached (Plugin.Awake).");

    configDebugGeneral = Config.Bind("General",
                                  "DebugMode",
                                  true,
                                  "Toggles logging more debug information to the log file.");

    CameraFeature.Initialize(Config);

    Harmony dataHarmony = new(DataHarmonyId);

    dataHarmony.CreateClassProcessor(typeof(Delta.FindModDataFolders)).Patch();
    dataHarmony.CreateClassProcessor(typeof(Delta.DeltaFileReadPatch)).Patch();


    CameraFeature.Start();


    // Log our awake here so we can see it in LogOutput.txt file
    Log.LogInfo($"Plugin {LCMPluginInfo.PLUGIN_NAME} GUID {LCMPluginInfo.PLUGIN_GUID} is loaded!");
  }

  private void OnDestroy()
  {
    CameraFeature.Stop();
  }

  public static void LogDebug(string text)
  {
    if (configDebugGeneral?.Value ?? false)
      Log?.LogDebug(text);
  }
}