# Custom Tab Proof of Concepts

## Usage

To run the Proof of Concepts, [Android Studio](https://developer.android.com/studio) is required. The applications can then either be executed in the built-in Android emulator or on a physical device.

## Applications

### Cross-Context State Inference (using Custom Tab Activity Hiding)

On start of the application, it is possible to define the URL to be launched in a Custom Tab. A click on the "Launch Custom Tab" button launches the Custom Tab, which loads the specified URL. The Custom Tab activity is immediately hidden by a new activity. When the user returns to the main activity, a list of all navigation events are shown. Additionally, a hidden WebView is loaded.

See `/state_inference`.

### HTTP Header Injection

After launching the application, users can specify one HTTP header-value pair that is added to the request inside the Custom Tab. The Custom Tab opens `https://httpbin.org/headers`, which reflects the HTTP request headers. Note that this attack required Chrome < 108, Edge < 108, or Brave < 1.46.

See `/header_injection`.

### Scroll Inference (using Web Content Hiding)

This PoC demonstrates the Scroll Inference attack combined with the Web Content Hiding attack. It can be used to check whether a website contains a specific string. Users can enter a URL and the target string. As soon as a scroll event is registered, the application displays the result.

See `/scroll_inference`.

### Bottom Bar Spoofing

This Proof of Concept shows how users can be tricked into clicking the bottom bar. When the user clicks on the bottom bar, the URL that is currently opened is displayed in the app.

See `/bottom_bar_spoofing`. 