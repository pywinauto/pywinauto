import os
from AppKit import NSWorkspace, NSWorkspaceLaunchDefault
from Foundation import NSURL

def debug_launch(app_name: str):
    workspace = NSWorkspace.sharedWorkspace()
    
    # Resolve the path (assuming it's in user Applications folder)
    if not app_name.endswith(".app"):
        app_name += ".app"
    app_path = os.path.expanduser(f"~/Applications/{app_name}")
    
    app_url = NSURL.fileURLWithPath_(app_path)
    
    print(f"[Debug] Attempting to launch path: {app_path}")
    print(f"[Debug] URL Exists: {os.path.exists(app_path)}")
    
    # Use the error-returning API. PyObjC translates NSError** into a tuple return
    # Syntax: launchApplicationAtURL_options_configuration_error_
    success, error = workspace.launchApplicationAtURL_options_configuration_error_(
        app_url,
        NSWorkspaceLaunchDefault,
        {}, # Empty configuration dictionary
        None # Pass None for the pointer; PyObjC maps it automatically
    )
    
    if not success:
        print("[FAIL] Application failed to launch.")
        if error:
            print(f"[ERROR CODE] {error.code()}")
            print(f"[DOMAIN] {error.domain()}")
            # localizedDescription provides the human-readable failure reason
            print(f"[REASON] {error.localizedDescription()}")
    else:
        print("[SUCCESS] Application launched successfully!")
        # success is an NSRunningApplication object if successful
        print(f"PID: {success.processIdentifier()}")

debug_launch("mousebuttons")
debug_launch("send_keys_test_app")
debug_launch("ControlsTestAppSB")
