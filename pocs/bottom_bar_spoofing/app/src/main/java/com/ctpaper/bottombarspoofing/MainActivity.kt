package com.ctpaper.bottombarspoofing

import android.app.PendingIntent
import android.content.ComponentName
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.browser.customtabs.*
import androidx.browser.customtabs.CustomTabsIntent.*


class MainActivity : AppCompatActivity() {
    var session: CustomTabsSession? = null
    var ctClient: CustomTabsClient? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val textView = findViewById<TextView>(R.id.urlText)

        val url: Uri? = intent.data
        if (url != null) {
            textView.text = url.toString()
        }

        val connection = object : CustomTabsServiceConnection() {
            override fun onCustomTabsServiceConnected(
                name: ComponentName,
                client: CustomTabsClient
            ) {
                session = client.newSession(null)
                ctClient = client
                client.warmup(0)
            }

            override fun onServiceDisconnected(componentName: ComponentName?) { }
        }

        CustomTabsClient.bindCustomTabsService(this, "com.android.chrome", connection)

        val button = findViewById<Button>(R.id.launchCT)
        button.setOnClickListener {
            open()
        }

    }

    /**
     * Opens the Custom Tab.
     */
    private fun open() {
        val ctIntent = Builder(session)
        val remoteView = RemoteViews(this@MainActivity.packageName, R.layout.remoteview)

        val bottomBarIntent = Intent(this@MainActivity, MainActivity::class.java)
        val bottomBarPendingIntent = PendingIntent.getActivity(this, 0, bottomBarIntent, PendingIntent.FLAG_MUTABLE)

        ctIntent.setSecondaryToolbarViews(remoteView, intArrayOf(
            R.id.remoteViewContainer,
            R.id.acceptButton
        ), bottomBarPendingIntent)
        ctIntent.setUrlBarHidingEnabled(false)

        ctIntent.setShareState(SHARE_STATE_OFF)

        val darkParams = CustomTabColorSchemeParams.Builder()
            .build()

        ctIntent.setColorScheme(COLOR_SCHEME_DARK)
            .setColorSchemeParams(COLOR_SCHEME_DARK, darkParams)
            .setDefaultColorSchemeParams(darkParams)

        val intent = ctIntent.build()
        val uri: String = "https://example.com"
        intent.launchUrl(this, Uri.parse(uri))
    }
}