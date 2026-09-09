using UnityEngine;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

public sealed class ESSDoorController : MonoBehaviour
{
    [SerializeField] private Transform[] hinges;
    [SerializeField] private float[] openAngles;
    [SerializeField] private Camera viewCamera;
    private bool[] open;

    private void Awake()
    {
        open = new bool[hinges.Length];
        for (int i = 0; i < hinges.Length; i++)
            open[i] = Quaternion.Angle(hinges[i].localRotation, Quaternion.identity) > 1f;
    }

    public void SetAll(bool value)
    {
        for (int i = 0; i < open.Length; i++) open[i] = value;
    }

    public bool ToggleDoor(Ray ray)
    {
        if (!Physics.Raycast(ray, out RaycastHit hit, 100f)) return false;
        for (int i = 0; i < hinges.Length; i++)
        {
            if (!hit.transform.IsChildOf(hinges[i])) continue;
            open[i] = !open[i];
            return true;
        }
        return false;
    }

    private void Update()
    {
        for (int i = 0; i < hinges.Length; i++)
            hinges[i].localRotation = Quaternion.RotateTowards(hinges[i].localRotation,
                Quaternion.Euler(0f, open[i] ? openAngles[i] : 0f, 0f), 140f * Time.deltaTime);
#if ENABLE_INPUT_SYSTEM
        if (Mouse.current == null || !Mouse.current.leftButton.wasPressedThisFrame) return;
        Vector2 point = Mouse.current.position.ReadValue();
#else
        if (!Input.GetMouseButtonDown(0)) return;
        Vector2 point = Input.mousePosition;
#endif
        if (point.y > Screen.height - 90f && point.x < 370f) return;
        ToggleDoor(viewCamera.ScreenPointToRay(point));
    }

    private void OnGUI()
    {
        GUI.Box(new Rect(12, 12, 350, 72), "ESS | 6 racks x 7 packs | Click a door");
        if (GUI.Button(new Rect(24, 43, 155, 30), "Open all doors")) SetAll(true);
        if (GUI.Button(new Rect(191, 43, 155, 30), "Close all doors")) SetAll(false);
    }
}
