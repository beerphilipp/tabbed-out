package com.ctpaper.stateinference.ui

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.ctpaper.stateinference.R
import com.ctpaper.stateinference.ui.overlay.OverlayFragment
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class OverlayActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.overlay_activity)
        val recipeFragment = OverlayFragment.newInstance()
        if (savedInstanceState == null) {
            supportFragmentManager.beginTransaction()
                .replace(R.id.container, recipeFragment)
                .commitNow()
        }
    }

    override fun onBackPressed() {
        navigateBack()
    }

    private fun navigateBack() {
        val intent = Intent(this, MainActivity::class.java)
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP)
        startActivity(intent)
    }
}