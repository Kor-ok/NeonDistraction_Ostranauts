using HarmonyLib;
using Ostranauts.Core;
using System;
using System.Linq;
using UnityEngine;

namespace NeonDistraction.SpaceTruckers.Graphical
{
  [HarmonyPatch(typeof(GameRenderer), nameof(GameRenderer.MainCamera), MethodType.Getter)]
  internal static class GameRendererMainCameraPatch
  {
    private static bool bCameraAngleRaised;
    private static Camera? mainCamera;
    private static Vector3 vOriginalEulerAngles;
    private static float fOriginalNearClipPlane;
    private static float fOriginalFarClipPlane;
    private static float fOriginalFieldOfView;
    private static bool bOriginalOrthographic;

    [HarmonyPostfix]
    private static void RaiseCameraAngle(Camera __result)
    {
      if (bCameraAngleRaised || __result == null)
        return;

      Vector3 vEulerAngles = __result.transform.eulerAngles;
      mainCamera = __result;
      vOriginalEulerAngles = vEulerAngles;
      fOriginalNearClipPlane = __result.nearClipPlane;
      fOriginalFarClipPlane = __result.farClipPlane;
      fOriginalFieldOfView = __result.fieldOfView;
      bCameraAngleRaised = true;
      bOriginalOrthographic = __result.orthographic;
      UpdateCameraSettings();
      CameraFeature.RefreshCameraInfo();

      Plugin.Log.LogInfo($"[SPACETRUCKERS] Raised the Main Camera angle by {CameraFeature.AngleDegrees.Value} degrees.");
    }

    internal static void UpdateCameraSettings()
    {
      if (!bCameraAngleRaised || mainCamera == null)
        return;

      mainCamera.transform.eulerAngles = new Vector3(
        vOriginalEulerAngles.x - CameraFeature.AngleDegrees.Value,
        vOriginalEulerAngles.y,
        vOriginalEulerAngles.z);
      mainCamera.nearClipPlane = CameraFeature.NearClipPlane.Value;
      mainCamera.farClipPlane = CameraFeature.FarClipPlane.Value;
      mainCamera.fieldOfView = CameraFeature.FieldOfView.Value;
      mainCamera.orthographic = CameraFeature.Orthographic.Value;
    }

    internal static string GetAllCamerasInfo()
    {
      Camera[] allCameras = Camera.allCameras;
      if (allCameras.Length == 0)
        return "No active cameras.";

      string strCameraInfo = string.Join(Environment.NewLine, allCameras
        .Where(camera => camera != null)
        .Select(camera => $"{camera.name}: near={camera.nearClipPlane}, far={camera.farClipPlane}, fov={camera.fieldOfView}"));

      // Log to console
      Plugin.LogDebug($"[SPACETRUCKERS] {strCameraInfo}");

      return strCameraInfo;
    }

    internal static void RestoreCamera()
    {
      if (mainCamera != null)
      {
        mainCamera.transform.eulerAngles = vOriginalEulerAngles;
        mainCamera.nearClipPlane = fOriginalNearClipPlane;
        mainCamera.farClipPlane = fOriginalFarClipPlane;
        mainCamera.fieldOfView = fOriginalFieldOfView;
        mainCamera.orthographic = bOriginalOrthographic;
      }

      mainCamera = null;
      bCameraAngleRaised = false;

      CameraFeature.RefreshCameraInfo();

      Plugin.Log.LogInfo("[SPACETRUCKERS] Restored the Main Camera angle.");
    }
  }
}
