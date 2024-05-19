package com.ctpaper.headerinjection

import android.content.ComponentName
import android.net.Uri
import android.os.Bundle
import android.provider.Browser
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.browser.customtabs.*
import androidx.browser.customtabs.CustomTabsIntent.*
import com.google.android.material.textfield.TextInputLayout


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
        val builder = Builder(session)
        builder.setUrlBarHidingEnabled(false)

        builder.setShareState(SHARE_STATE_OFF)

        val darkParams = CustomTabColorSchemeParams.Builder()
            .build()

        builder.setColorScheme(COLOR_SCHEME_DARK)
            .setColorSchemeParams(COLOR_SCHEME_DARK, darkParams)
            .setDefaultColorSchemeParams(darkParams)

        val ctIntent = builder.build()

        // Get header and key values
        val headerKey: String = findViewById<TextInputLayout>(R.id.header_key).editText?.text.toString()
        val headerValue: String = findViewById<TextInputLayout>(R.id.header_value).editText?.text.toString()

        // Create the header
        val headers = Bundle()
        headers.putString("sec-ch-ua", "\n$headerKey: $headerValue")
        ctIntent.intent.putExtra(Browser.EXTRA_HEADERS, headers)
        findViewById<TextView>(R.id.header_key)

        // Launch the CT
        ctIntent.launchUrl(this, Uri.parse("https://httpbin.org/headers"))
    }
}