package com.ctpaper.scrollinference

import android.content.ComponentName
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.os.Handler
import android.util.Log
import android.util.TypedValue
import android.view.ViewTreeObserver
import android.widget.Button
import android.widget.RemoteViews
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.content.res.AppCompatResources
import androidx.browser.customtabs.*
import androidx.browser.customtabs.CustomTabsIntent.*
import androidx.core.graphics.drawable.toBitmap
import com.google.android.material.textfield.TextInputLayout


class MainActivity : AppCompatActivity() {
    var session: CustomTabsSession? = null
    var ctClient: CustomTabsClient? = null
    var bottomBarHeight: Int? = null
    var handler: Handler = Handler()
    var downwardScroll: Boolean? = null


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val callback = object : CustomTabsCallback() {
            override fun extraCallback(callbackName: String, args: Bundle?) {
                Log.e("TAG", callbackName)
                if (args != null) {

                    if (callbackName == "onVerticalScrollEvent") {
                        val isUp: Boolean = args.get("isDirectionUp") as Boolean
                        if (!isUp) {
                            // The user scrolled downwards, thus potentially interfering with the maximum scroll result
                            Log.i("TAG", "The user scrolled downwards.")
                            downwardScroll = true
                            openResult(false, -1)
                        } else {
                            Log.i("TAG", "The user scrolled upwards")
                            // The user scrolled upwards.
                            // We wait 500ms for the onGreatestPercentageIncreased event.
                            // If we don't receive this event, the user is at the start of the page

                            handler.postDelayed({
                                openResult(true, 0)
                            }, 500)


                            // Alternatively, we can use the extraCommand function to query the greatest scroll percentage:

                            /*val resultBundle = ctClient!!.extraCommand("getGreatestScrollPercentage", null)
                            val scrollPosition: Int = resultBundle!!.get("greatestScrollPercentage") as Int
                            openResult(true, scrollPosition)*/

                        }
                    }

                    if (callbackName == "onGreatestScrollPercentageIncreased" && downwardScroll != true) {
                        Log.i("TAG", "greatest!!")
                        handler.removeCallbacksAndMessages(null)
                        val scrollPosition: Int = args.get("scrollPercentage") as Int
                        openResult(true, scrollPosition)
                    }

                }
            }
        }

        val connection = object : CustomTabsServiceConnection() {
            override fun onCustomTabsServiceConnected(
                name: ComponentName,
                client: CustomTabsClient
            ) {
                session = client.newSession(callback)
                ctClient = client
                client.warmup(0)
            }

            override fun onServiceDisconnected(componentName: ComponentName?) { }
        }

        CustomTabsClient.bindCustomTabsService(this, "com.android.chrome", connection)

        // Get the height of the web content
        val view = findViewById<TextView>(R.id.helloWorldTex)
        view.viewTreeObserver.addOnGlobalLayoutListener(object :
            ViewTreeObserver.OnGlobalLayoutListener {
            override fun onGlobalLayout() {
                view.viewTreeObserver.removeOnGlobalLayoutListener(this)
                bottomBarHeight = view.height - 1
            }
        })

        val button = findViewById<Button>(R.id.launchCT)
        button.setOnClickListener {
            open()
        }

    }

    /**
     * Opens the result activity.
     */
    private fun openResult(gotResult: Boolean, scrollPosition: Int) {
        val intent = Intent(this@MainActivity, ResultActivity::class.java)
        intent.putExtra("gotResult", gotResult)
        intent.putExtra("scrollPosition", scrollPosition)
        this@MainActivity.startActivity(intent)
    }

    /**
     * Opens the Custom Tab.
     */
    private fun open() {
        val ctIntent = Builder(session)
        val remoteView = RemoteViews(this@MainActivity.packageName, R.layout.remoteview)
        remoteView.setViewLayoutHeight(R.id.remoteViewContainer, bottomBarHeight!!.toFloat(), TypedValue.COMPLEX_UNIT_PX)
        ctIntent.setSecondaryToolbarViews(remoteView, intArrayOf(1), null)


        val darkParams = CustomTabColorSchemeParams.Builder()
            .build()

        ctIntent.setColorScheme(COLOR_SCHEME_DARK)
            .setColorSchemeParams(COLOR_SCHEME_DARK, darkParams)
            .setDefaultColorSchemeParams(darkParams)

        // Close button
        AppCompatResources.getDrawable(this, R.drawable.baseline_arrow_back_24)?.let {
            ctIntent.setCloseButtonIcon(it.toBitmap())
        }

        ctIntent.setShareState(SHARE_STATE_OFF)
        ctIntent.setUrlBarHidingEnabled(false)

        val intent = ctIntent.build()
        val url = findViewById<TextInputLayout>(R.id.url).editText!!.text.toString()
        val string: String = findViewById<TextInputLayout>(R.id.string).editText!!.text.toString()
        val encodedString = java.net.URLEncoder.encode(string, "utf-8")

        val uri: String = "${url}#:~:text=${encodedString}"
        intent.launchUrl(this, Uri.parse(uri))
    }
}