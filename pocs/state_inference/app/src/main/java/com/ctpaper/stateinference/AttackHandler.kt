package com.ctpaper.stateinference

import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.net.Uri
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.webkit.JavascriptInterface
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.browser.customtabs.*
import androidx.core.content.ContextCompat.startActivity
import com.ctpaper.stateinference.data.NavigationEvent
import com.ctpaper.stateinference.ui.main.MainViewModel
import kotlinx.coroutines.runBlocking

class AttackHandler(
    val context: Context,
    val viewModel: MainViewModel,
    private val webView: WebView) {

    lateinit var callback: CustomTabsCallback
    lateinit var connection: CustomTabsServiceConnection
    var session: CustomTabsSession? = null

    var startTime: Long? = null
    var endTime: Long? = null
    var isFailed: Boolean? = null

    var webViewStartTime: Long? = null

    private val packageNameChrome = "com.android.chrome"
    private var packageName = packageNameChrome
    var intent: Intent? = null
    private var currentUrl: String = "https://example.com"

    private var webViewLoadingTime: Float? = null

    init {
        setupCustomTab()
        setupWebView()
    }

    private fun setupCustomTab() {
        callback = object : CustomTabsCallback() {
            override fun onNavigationEvent(navigationEvent: Int, extras: Bundle?) {
                when(navigationEvent) {
                    TAB_SHOWN -> {
                        this@AttackHandler.openOverlay()
                    }
                    NAVIGATION_STARTED -> {
                        startTime = extras!!.getLong("timestampUptimeMillis")
                        viewModel.addEvent(
                            NavigationEvent(
                            packageName,
                            "NAVIGATION_STARTED",
                            currentUrl
                        )
                        )
                    }
                    NAVIGATION_FINISHED -> {
                        endTime = extras!!.getLong("timestampUptimeMillis")
                        if (isFailed == null) {
                            isFailed = false
                        }
                        onLoadingFinished()

                    }
                    NAVIGATION_FAILED -> {
                        isFailed = true
                    }
                    else -> { }
                }
            }
        }

        connection = object : CustomTabsServiceConnection() {
            override fun onCustomTabsServiceConnected(
                    name: ComponentName,
                    client: CustomTabsClient
            ) {
                session = client.newSession(callback)
                client.warmup(0)
            }

            override fun onServiceDisconnected(componentName: ComponentName?) { }
        }
        packageName = packageNameChrome

        CustomTabsClient.bindCustomTabsService(context, packageName, connection)
    }

    private fun setupWebView() {
        WebView.setWebContentsDebuggingEnabled(true)
        webView.settings.javaScriptEnabled = true
        webView.webViewClient = WebViewClient()
        webView.webViewClient = object: WebViewClient() {

            override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
                webViewStartTime = System.currentTimeMillis()
                super.onPageStarted(view, url, favicon)
            }

            override fun onPageFinished(view: WebView?, url: String?) {
                val webViewDuration = System.currentTimeMillis() - webViewStartTime!!
                viewModel.addEvent(
                    NavigationEvent(
                        "WebView",
                        "WEBVIEW_LOADED",
                        currentUrl,
                        webViewDuration
                    )
                )

            }
        }
    }

    fun navigate(intent: Intent) {
        currentUrl = viewModel.url.value?:"https://example.com"
        startTime = null
        endTime = null
        isFailed = null
        this.intent = intent
        val builder: CustomTabsIntent.Builder = CustomTabsIntent.Builder(session)
        val cctIntent: CustomTabsIntent = builder.build()

        loadInWebView()
        cctIntent.launchUrl(context, Uri.parse(currentUrl))
    }

    private fun openOverlay() {
        if (intent != null) {
            startActivity(context, intent!!, null)
        }
    }

    private fun onLoadingFinished() {
        if (isFailed == true) {
            viewModel.addEvent(
                NavigationEvent(
                    packageName,
                    "NAVIGATION_FAILED_AND_FINISHED",
                    currentUrl,
                    endTime!! - startTime!!
                )
            )
        } else {
            viewModel.addEvent(
                NavigationEvent(
                    packageName,
                    "NAVIGATION_FINISHED_2XX_3XX",
                    currentUrl,
                    endTime!! - startTime!!
                )
            )
        }
    }

    private fun loadInWebView() {
        webViewLoadingTime = null
        webView.loadUrl(currentUrl)
    }

}