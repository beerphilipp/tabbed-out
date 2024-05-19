package com.ctpaper.scrollinference

import android.os.Bundle
import android.util.Log
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity


class ResultActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_result)

        val gotResult = intent.getBooleanExtra("gotResult", false)
        val scrollPosition = intent.getIntExtra("scrollPosition", -1);
        val view = findViewById<TextView>(R.id.scroll_pos_result)
        if (!gotResult) {
            view.text = "Could not reliably determine scroll position since the user scrolled down."
        } else {
            if (scrollPosition > 0) {
                view.text = "Text appears on the website"
            } else {
                view.text = "Text does not appear on the website"
            }
        }
    }
}