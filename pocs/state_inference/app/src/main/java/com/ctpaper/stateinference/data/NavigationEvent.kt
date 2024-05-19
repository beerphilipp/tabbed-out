package com.ctpaper.stateinference.data

/**
 * This class represents a navigation event that occurs in a WebView or Custom Tab.
 */
data class NavigationEvent(
    val browser: String,
    val event: String,
    val url: String,
    val duration: Long? = null
) {
    override fun toString(): String {
        return "$event \n** $browser \n** $url; \n** Duration: $duration"
    }
}
