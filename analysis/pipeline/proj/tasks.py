import os
import json
import glob
import shutil

from .celery import app
from celery.utils.log import get_task_logger
from celery.exceptions import SoftTimeLimitExceeded

from proj import APK_DIR, RES_DIR, TMP_PATH, APKEDITOR_PATH

from androguard import misc

logger = get_task_logger(__name__)

@app.task(soft_time_limit = 60 * 15)
def analyze_apk(package_name, split_files):
    try:
        logger.info("Analyzing package {}".format(package_name))
        
        result = { 
            'package_name': package_name
        }
        
        result['source'] = create_merged_apk(package_name, split_files)
        needs_removal = False
        if (result['source'] == 'MULTIPLE_APKS'):
            apk_path = os.path.join(TMP_PATH, package_name + "_merged.apk")
            needs_removal = True
        else:
            apk_path = get_apk_path(package_name)
            if (result['source'] == 'SINGLE_APK_E'):
                needs_removal = True

        a, _, dx = misc.AnalyzeAPK(apk_path)

        result['ct_session_intent_filter'] = find_intent_filter(a)
        result['uses_ct'] = find_ct_string(dx)

        if not (result['uses_ct'] or result['ct_session_intent_filter']):
            # If neither an intent filter could be found nor a CT string, we stop the analysis
            return write_result_to_file(package_name, result)
        
        result['ct_feature_strings'] = find_feature_strings(dx)
        result['ct_session_functions'] = find_session_functions(dx)
        result['ct_client_functions'] = find_client_functions(dx)
        result['ct_builder_functions'] = find_builder_functions(dx)
        result['ct_callbacks_overwrite'] = find_callback_overwrite(dx)
        result['ct_launch_url_call'] = find_launch_url_call(dx)
        result['ct_fuzzy'] = fuzz_search_ct_classnames(dx)
        result['ct_callback_fuzzy'] = fuzz_search_ct_callback_classnames(dx)

        if (needs_removal):
            remove_tmp(package_name)

        return write_result_to_file(package_name, result)
            
    except SoftTimeLimitExceeded:
        if (needs_removal):
            remove_tmp(package_name)
        logger.error("A timout occurred for package {}".format(package_name))
        result['error'] = 'TIMEOUT'
        return write_result_to_file(package_name, result)

    except FileNotFoundError:
        if (needs_removal):
            remove_tmp(package_name)
        logger.info("APK for {} could not be found at {}".format(package_name, apk_path))
        result['error'] = 'APK_NOT_FOUND'
        return write_result_to_file(package_name, result)

    except Exception as e:
        if (needs_removal):
            remove_tmp(package_name)
        logger.error("An unexpected error occurred while analyzing {}: {}".format(package_name, repr(e)))
        result['error'] = 'UNSPECIFIED_ERROR'
        result['error_details'] = repr(e)
        return write_result_to_file(package_name, result)



def get_apk_path(package_name):
    return os.path.join(APK_DIR, "{}.apk".format(package_name))


"""
    Checks if the CustomTabsService intent filter is registered in the app's manifest.
"""
def find_intent_filter(a):
    logger.info("Finding intent filter")
    manifest_tree = a.get_android_manifest_xml()
    if manifest_tree == None:
        return {
            'error': 'MANIFEST_MISSING'
        }
    action_intents = manifest_tree.xpath("/manifest/queries/intent/action[@*='android.support.customtabs.action.CustomTabsService']")
    return len(action_intents) > 0

"""
    Searches for the 'android.support.customtabs.extra.SESSION' string.
"""
def find_ct_string(dx):
    try:
        all_ct_strings = dx.find_strings("android.support.customtabs.extra.SESSION")
        return len(list(all_ct_strings)) > 0
    except Exception as e:
        logger.error("An error occurred while finding the CT string: {}".format(repr(e)))
        return {
            'error': 'UNSPECIFIED_ERROR',
            'details': repr(e)
        }

"""
    Searches for CT feature strings in the source code.
"""
def find_feature_strings(dx):
    logger.info("Finding feature strings")
    try:
        feature_extras = [
            "android.support.customtabs.extra.SESSION",
            "android.support.customtabs.extra.SESSION_ID",
            "android.support.customtabs.extra.user_opt_out", 
            "androidx.browser.customtabs.extra.COLOR_SCHEME", 
            "android.support.customtabs.extra.TOOLBAR_COLOR",
            "android.support.customtabs.extra.ENABLE_URLBAR_HIDING", 
            "android.support.customtabs.extra.CLOSE_BUTTON_ICON", 
            "android.support.customtabs.extra.TITLE_VISIBILITY",
            "android.support.customtabs.extra.ACTION_BUTTON_BUNDLE",
            "android.support.customtabs.extra.TOOLBAR_ITEMS", 
            "android.support.customtabs.extra.SECONDARY_TOOLBAR_COLOR", 
            "android.support.customtabs.customaction.ICON", 
            "android.support.customtabs.customaction.DESCRIPTION", 
            "android.support.customtabs.customaction.PENDING_INTENT",
            "android.support.customtabs.extra.TINT_ACTION_BUTTON", 
            "android.support.customtabs.extra.MENU_ITEMS", 
            "android.support.customtabs.customaction.MENU_ITEM_TITLE", 
            "android.support.customtabs.extra.EXIT_ANIMATION_BUNDLE", 
            "androidx.browser.customtabs.extra.SHARE_STATE", 
            "android.support.customtabs.extra.SHARE_MENU_ITEM", 
            "android.support.customtabs.extra.EXTRA_REMOTEVIEWS", 
            "android.support.customtabs.extra.EXTRA_REMOTEVIEWS_VIEW_IDS", 
            "android.support.customtabs.extra.EXTRA_REMOTEVIEWS_PENDINGINTENT",
            "android.support.customtabs.extra.EXTRA_REMOTEVIEWS_CLICKED_ID", 
            "android.support.customtabs.extra.EXTRA_ENABLE_INSTANT_APPS", 
            "androidx.browser.customtabs.extra.COLOR_SCHEME_PARAMS",
            "androidx.browser.customtabs.extra.NAVIGATION_BAR_COLOR", 
            "androidx.browser.customtabs.extra.NAVIGATION_BAR_DIVIDER_COLOR", 
            "android.support.customtabs.customaction.ID", 
            "android.support.customtabs.action.CustomTabsService", 
            "androidx.browser.customtabs.category.NavBarColorCustomization", 
            "androidx.browser.customtabs.category.ColorSchemeCustomization", 
            "androidx.browser.trusted.category.TrustedWebActivities", 
            "androidx.browser.trusted.category.WebShareTargetV2", 
            "androidx.browser.trusted.category.ImmersiveMode", 
            "android.support.customtabs.otherurls.URL",
            "androidx.browser.customtabs.SUCCESS", 
            "androidx.browser.REDIRECT_ENDPOINT", 
            "android.support.customtabs.PARALLEL_REQUEST_REFERRER", 
            "android.support.customtabs.PARALLEL_REQUEST_REFERRER_POLICY",
            "android.support.customtabs.PARALLEL_REQUEST_URL", 
            "androidx.browser.RESOURCE_PREFETCH_URL_LIST", 
            "androidx.browser.customtabs.extra.EXTRA_ACTIVITY_SIDE_SHEET_POSITION",
            "androidx.browser.customtabs.extra.EXTRA_ACTIVITY_SIDE_SHEET_SLIDE_IN_BEHAVIOR", 
            "android.support.customtabs.extra.KEEP_ALIVE", 
            "org.chromium.chrome.browser.customtabs.MEDIA_VIEWER_URL",
            "org.chromium.chrome.browser.customtabs.EXTRA_ENABLE_EMBEDDED_MEDIA_EXPERIENCE", 
            "org.chromium.chrome.browser.customtabs.EXTRA_UI_TYPE", 
            "org.chromium.chrome.browser.customtabs.EXTRA_INITIAL_BACKGROUND_COLOR",
            "org.chromium.chrome.browser.customtabs.EXTRA_DISABLE_STAR_BUTTON", 
            "org.chromium.chrome.browser.customtabs.EXTRA_DISABLE_DOWNLOAD_BUTTON", 
            "org.chromium.chrome.browser.customtabs.EXTRA_BROWSER_LAUNCH_SOURCE",
            "android.support.customtabs.extra.SEND_TO_EXTERNAL_HANDLER", 
            "androidx.browser.customtabs.extra.TRANSLATE_LANGUAGE", 
            "androidx.browser.customtabs.extra.AUTO_TRANSLATE_LANGUAGE",
            "org.chromium.chrome.browser.customtabs.AGA_EXPERIMENT_IDS", 
            "org.chromium.chrome.browser.customtabs.EXPERIMENTS_ENABLE", 
            "org.chromium.chrome.browser.customtabs.EXPERIMENTS_DISABLE", 
            "androidx.browser.customtabs.extra.INITIAL_ACTIVITY_HEIGHT_IN_PIXEL", 
            "androidx.browser.customtabs.extra.INITIAL_ACTIVITY_HEIGHT_PX", 
            "androidx.browser.customtabs.extra.INITIAL_ACTIVITY_WIDTH_PX",
            "androix.browser.customtabs.extra.ENABLE_BACKGROUND_INTERACTION", 
            "androix.browser.customtabs.extra.EXTRA_ACTIVITY_SIDE_SHEET_ENABLE_MAXIMIZATION", 
            "androidx.browser.customtabs.extra.ACTIVITY_HEIGHT_RESIZE_BEHAVIOR",
            "androidx.browser.customtabs.extra.ACTIVITY_SIDE_SHEET_BREAKPOINT_DP", 
            "androidx.browser.customtabs.extra.ACTIVITY_SIDE_SHEET_DECORATION_TYPE", 
            "androidx.browser.customtabs.extra.TOOLBAR_CORNER_RADIUS_IN_PIXEL", 
            "androidx.browser.customtabs.extra.SECONDARY_TOOLBAR_SWIPE_UP_ACTION",
            "com.android.chrome.tab_id",
            "com.android.chrome.parent_tab_id",
            "com.android.chrome.parent_intent",
            "org.chromium.chrome.browser.parent_componen",
            "com.google.chrome.transition_type",
            "com.google.chrome.transition_bookmark_id",
            "com.android.chrome.original_intent",
            "com.android.chrome.invoked_from_fre",
            "com.android.chrome.invoked_from_shortcut",
            "com.android.chrome.invoked_from_app_widget",
            "org.chromium.chrome.browser.incognito.invoked_from_launch_new_incognito_tab",
            "org.chromium.chrome.browser.activity_referrer",
            "org.chromium.chrome.browser.calling_activity_package",
            "org.chromium.chrome.browser.referrer_id",
            "android.support.browser.extra.referrer_policy",
            "org.chromium.chrome.browser.additional_urls",
            "org.chromium.chrome.browser.open_additional_urls_in_tab_group",
            "org.chromium.chrome.browser.open_regular_overview_mode",
            "org.chromium.chrome.browser.timestamp",
            "org.chromium.chrome.browser.window_id",
            "org.chromium.chrome.browser.tab_launch_type",
            "org.chromium.chrome.browser.data_hash",
            "org.chromium.chrome.browser.incognito_mode",
            "com.android.chrome.post_data",
            "com.android.chrome.post_data_type",
            "com.android.chrome.from_open_in_browser",
            "com.android.chrome.prefer_new",
            "org.chromium.chrome.browser.customtabs.EXTRA_INCOGNITO_CCT_CALLER_ID",
            "org.chromium.chrome.browser.started_chrome_task",
            "androidx.browser.customtabs.extra.CLOSE_BUTTON_POSITION", 
            "com.google.android.apps.chrome.EXTRA_OPEN_NEW_INCOGNITO_TAB",
            "android.support.customtabs.extra.ADDITIONAL_TRUSTED_ORIGIN",
            "androidx.browser.trusted.extra.SHARE_TARGET",
            "androidx.browser.trusted.extra.DISPLAY_MODE",
            "androidx.browser.trusted.extra.SCREEN_ORIENTATION", 
            "android.support.customtabs.extra.LAUNCH_AS_TRUSTED_WEB_ACTIVITY",
            "android.support.customtabs.action.ACTION_MANAGE_TRUSTED_WEB_ACTIVITY_DATA", 
            "com.android.browser.headers",
            "browser.initialZoomLevel"
            ] # same here
        result = {}
        for extra in feature_extras:
            classnames = []
            strings = dx.find_strings(extra)
            for string in strings:
                for _, meth in string.get_xref_from():
                    classname = meth.class_name
                    classnames.append(str(classname))
            result[extra] = classnames
        return result
    except Exception as e:
        logger.error("An error occurred while finding CT feature string: {}".format(repr(e)))
        return {
            'error': 'UNSPECIFIED_ERROR',
            'details': repr(e)
        }

"""
    Searches for the usage of 'CustomTabsSession' functions.
"""
def find_session_functions(dx):
    logger.info("Finding session function")
    try:
        functions = [
            "mayLaunchUrl", 
            "setActionButton", 
            "setSecondaryToolbarViews", 
            "setToolbarItem", 
            "requestPostMessageChannel", 
            "postMessage", 
            "validateRelationship", 
            "receiveFile"
            ]

        result = { }
        for f in functions:
            methods = dx.find_methods("Landroidx/browser/customtabs/CustomTabsSession", f)
            callees = []
            for m in methods:
                xrefs = m.get_xref_from()
                for _, meth , _ in xrefs:
                    calling_class_name = meth.class_name
                    if (not calling_class_name.startswith("Landroidx/browser")): 
                        # we exclude functions that are called form `androidx.browser` library code
                        callees.append(str(calling_class_name))
            result[f] = callees
        return result
    except Exception as e:
        logger.error("An error occurred while finding CT session function: {}".format(repr(e)))
        return {
            'error': 'UNSPECIFIED_ERROR',
            'details': repr(e)
        }

"""
    Searches for the usage of 'CustomTabsClient' functions.
"""
def find_client_functions(dx):
    logger.info("Finding client functions")
    try:
        functions = [
            "bindCustomTabsService", 
            "bindCustomTabsServicePreservePriority", 
            "getPackageName", 
            "connectAndInitialize", 
            "warmup", 
            "newSession", 
            # "newPendingSession", we omit this, since this can only be called from Library code
            "extraCommand", 
            # "attachSession", we omit this, since this can only be called form Library code
            ]
            
        result = { }
        for f in functions:
            methods = dx.find_methods("Landroidx/browser/customtabs/CustomTabsClient", f)
            callees = []
            for m in methods:
                xrefs = m.get_xref_from()
                for _, meth , _ in xrefs:
                    calling_class_name = meth.class_name
                    if (not calling_class_name.startswith("Landroidx/browser")): 
                        # we exclude functions that are called form `androidx.browser` library code
                            callees.append(str(calling_class_name))
            result[f] = callees
        return result
    except Exception as e:
        logger.error("An error occurred while finding CT client functions: {}".format(repr(e)))
        return {
            'error': 'UNSPECIFIED_ERROR',
            'details': repr(e)
        }

"""
    Searches for the usage of CustomTabsIntent$Builder functions.
"""
def find_builder_functions(dx):
    logger.info("Finding builder functions")
    try:
        functions = [
            "setSession",
            # "setPendingSession", we omit this, since this can only be called from Library code
            "setToolbarColor", #deprecated as of (at least) 1.5.0
            "enableUrlBarHiding", # deprecated
            "setUrlBarHidingEnabled",
            "setCloseButtonIcon",
            "setShowTitle",
            "addMenuItem",
            "addDefaultShareMenuItem", # deprecated
            "setDefaultShareMenuItemEnabled", # deprecated
            "setShareState",
            "setActionButton",
            "addToolbarItem", # deprecated
            "setSecondaryToolbarColor", # deprecated
            "setNavigationBarColor", # deprecated
            "setNavigationBarDividerColor", # deprecated
            "setSecondaryToolbarViews",
            "setInstantAppsEnabled",
            "setStartAnimations",
            "setExitAnimations",
            "setColorScheme",
            "setColorSchemeParams",
            "setDefaultColorSchemeParams",
            "setInitialActivityHeightPx",
            "setToolbarCornerRadiusDp",
            "setCloseButtonPosition",
        ]

        result = { }
        for f in functions:
            methods = dx.find_methods("Landroidx/browser/customtabs/CustomTabsIntent\$Builder", f) # we need to escape the dollar sign, since this is a regex
            callees = []
            for m in methods:
                xrefs = m.get_xref_from()
                for _, meth , _ in xrefs:
                    calling_class_name = meth.class_name
                    if (not calling_class_name.startswith("Landroidx/browser")): 
                        # we exclude functions that are called form `androidx.browser` library code
                        callees.append(str(calling_class_name))
                
            result[f] = callees
        return result
    except Exception as e:  
        logger.error("An error occurred while finding CT builder functions: {}".format(repr(e)))
        return {
            'error': 'UNSPECIFIED_ERROR',
            'details': repr(e)
        }

"""
    Searches for calls to 'launchUrl'.
"""
def find_launch_url_call(dx):
    logger.info("Finding launchUrl call")
    try:
        callees = []
        methods = dx.find_methods("Landroidx/browser/customtabs/CustomTabsIntent", "launchUrl")
        for m in methods:
            xrefs = m.get_xref_from()
            for _, meth , _ in xrefs:
                calling_class_name = meth.class_name
                if (not calling_class_name.startswith("Landroidx/browser")): 
                    # we exclude functions that are called form `androidx.browser` library code
                    callees.append(str(calling_class_name))
        return callees
    except Exception as e:
        logger.error("An error occurred while finding the launchUrl call: {}".format(repr(e)))
        return {
            'error': 'GENERIC',
            'details': repr(e)
        }

"""
    Searches for overwrites of the CustomTabsCallback class.
"""
def find_callback_overwrite(dx):
    logger.info("Finding callback overwrites")
    try:
        classes = []
        for c in dx.get_classes():
            if c.is_external():
                continue
            if (c.orig_class.get_superclassname().startswith("Landroidx/browser/customtabs/CustomTabsCallback")):
                if (not c.orig_class.name.startswith("Landroidx/browser")):
                    classes.append(str(c.name))
        return classes
    except Exception as e:
        logger.error("An error occurred while finding CT overwrites: {}".format(repr(e)))
        return {
            'error': 'UNSPECIFIED_ERROR',
            'details': repr(e)
        }

"""
    Searches for class names that contain 'CustomTab', excluding android* classes.
"""
def fuzz_search_ct_classnames(dx):
    try:
        result = []
        ct_classes = dx.find_classes("^(?!Landroid).*CustomTab.*")
        for c in ct_classes:
            result.append(str(c.name))
        return result
    except Exception as e:
        return {
            'error': 'UNSPECIFIED_ERROR',
            'details': repr(e)
        }

"""
    Searches for class names that contain 'CustomTab' and 'Callback', excluding android* classes.
"""
def fuzz_search_ct_callback_classnames(dx):
    try:
        result = []
        ct_classes = dx.find_classes("^(?!Landroid).*CustomTab.*Callback.*")
        for c in ct_classes:
            result.append(str(c.name))
        return result
    except Exception as e:
        return {
            'error': 'UNSPECIFIED_ERROR',
            'details': repr(e)
        }

"""
    Uses https://github.com/REAndroid/APKEditor to merge split apks.
"""
def create_merged_apk(package_name, split_files):
    logger.info("Creating merged apk")
    try:
        if split_files == None or len(split_files) == 0:
            return 'SINGLE_APK'
        apk = os.path.join(APK_DIR, package_name + ".apk")
        tmp_apks_path = os.path.join(TMP_PATH, package_name)
        os.mkdir(tmp_apks_path)
        for file in split_files:
            shutil.copy2(os.path.join(APK_DIR, file), tmp_apks_path)
        shutil.copy2(apk, tmp_apks_path)
        os.system("java -jar {} m -i {}".format(APKEDITOR_PATH, tmp_apks_path))
        return 'MULTIPLE_APKS'
    except Exception as e:
        logger.error("An error occurred while merging apks: {}".format(e))
        return 'SINGLE_APK_E'

"""
    Removes the temporary files that were created to merge the apks.
"""
def remove_tmp(package_name):
    try:
        shutil.rmtree(os.path.join(TMP_PATH, package_name))
        os.remove(os.path.join(TMP_PATH, package_name + "_merged.apk"))
    except Exception as e:
        logger.error("Could not remove tmp folder: {}".format(e))
        return

"""
    Writes the report of the analysis to the output file.
"""
def write_result_to_file(package_name, result):
    try:
        logger.info("Writing result to file for {}".format(package_name))
        res_file = os.path.join(RES_DIR, "{}.res.json".format(package_name))
        with open(res_file, 'w') as f:
            json.dump(result, f, indent=4)
        return result
    except Exception as e:
        return { }