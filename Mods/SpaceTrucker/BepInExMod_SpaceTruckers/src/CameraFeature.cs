using BepInEx.Configuration;
using HarmonyLib;
using System;

namespace NeonDistraction.SpaceTruckers.Graphical
{
  internal static class CameraFeature
  {
    private const string HarmonyId = LCMPluginInfo.PLUGIN_GUID + ".camera";

    internal static ConfigEntry<bool> IsEnabled = null!;
    internal static ConfigEntry<float> AngleDegrees = null!;
    internal static ConfigEntry<float> NearClipPlane = null!;
    internal static ConfigEntry<float> FarClipPlane = null!;
    internal static ConfigEntry<float> FieldOfView = null!;
    internal static ConfigEntry<bool> Orthographic = null!;
    internal static ConfigEntry<string> AllCameras = null!;

    private static Harmony? harmony;

    internal static void Initialize(ConfigFile config)
    {
      IsEnabled = config.Bind("General",
                              "CameraAngleRaised",
                              true,
                              "Toggles changes to the camera angle.");

      AngleDegrees = config.Bind("Camera",
                                 "AngleDegrees",
                                 15f,
                                 new ConfigDescription("Raises the main camera angle in degrees.", new AcceptableValueRange<float>(0f, 90f)));

      NearClipPlane = config.Bind("Camera",
                                  "NearClipPlane",
                                  0.001f,
                                  new ConfigDescription("Sets the main camera near clipping plane.", new AcceptableValueRange<float>(0.001f, 10f)));

      FarClipPlane = config.Bind("Camera",
                                 "FarClipPlane",
                                 1000f,
                                 new ConfigDescription("Sets the main camera far clipping plane.", new AcceptableValueRange<float>(1f, 100000f)));

      FieldOfView = config.Bind("Camera",
                                "FieldOfView",
                                60f,
                                new ConfigDescription("Sets the main camera field of view.", new AcceptableValueRange<float>(1f, 179f)));

      Orthographic = config.Bind("Camera",
                                 "Orthographic",
                                 true,
                                 "Toggles the main camera between perspective and orthographic projection.");

      AllCameras = config.Bind("Camera",
                               "AllCameras",
                               "No active cameras.",
                               "Informational: lists all currently active Unity cameras.");
    }

    internal static void Start()
    {
      IsEnabled.SettingChanged += OnEnabledChanged;
      AngleDegrees.SettingChanged += OnCameraSettingChanged;
      NearClipPlane.SettingChanged += OnCameraSettingChanged;
      FarClipPlane.SettingChanged += OnCameraSettingChanged;
      FieldOfView.SettingChanged += OnCameraSettingChanged;
      Orthographic.SettingChanged += OnCameraSettingChanged;
      SetEnabled(IsEnabled.Value);
    }

    internal static void Stop()
    {
      IsEnabled.SettingChanged -= OnEnabledChanged;
      AngleDegrees.SettingChanged -= OnCameraSettingChanged;
      NearClipPlane.SettingChanged -= OnCameraSettingChanged;
      FarClipPlane.SettingChanged -= OnCameraSettingChanged;
      FieldOfView.SettingChanged -= OnCameraSettingChanged;
      Orthographic.SettingChanged -= OnCameraSettingChanged;
      SetEnabled(false);
    }

    internal static void RefreshCameraInfo()
    {
      AllCameras.Value = GameRendererMainCameraPatch.GetAllCamerasInfo();
    }

    private static void OnEnabledChanged(object sender, EventArgs e)
    {
      SetEnabled(IsEnabled.Value);
    }

    private static void OnCameraSettingChanged(object sender, EventArgs e)
    {
      GameRendererMainCameraPatch.UpdateCameraSettings();
      RefreshCameraInfo();
    }

    private static void SetEnabled(bool enabled)
    {
      if (enabled)
      {
        if (harmony != null)
          return;

        harmony = new Harmony(HarmonyId);
        harmony.CreateClassProcessor(typeof(GameRendererMainCameraPatch)).Patch();
        Plugin.Log.LogInfo("[SPACETRUCKERS] Camera patches enabled.");
        return;
      }

      if (harmony == null)
        return;

      GameRendererMainCameraPatch.RestoreCamera();
      harmony.UnpatchSelf();
      harmony = null;
      RefreshCameraInfo();
      Plugin.Log.LogInfo("[SPACETRUCKERS] Camera patches disabled.");
    }
  }
}
