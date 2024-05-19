package com.ctpaper.stateinference.ui.main

import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import com.ctpaper.stateinference.data.NavigationEvent
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject

@HiltViewModel
class MainViewModel @Inject constructor() : ViewModel() {
    val url = MutableLiveData<String>()
    val events = MutableLiveData<ArrayList<NavigationEvent>>()

    fun start() {
        events.value = ArrayList()
    }

    fun addEvent(event: NavigationEvent) {
        val newList = ArrayList(events.value)
        newList.add(event)
        events.postValue(newList)
    }

    fun formatEvents(): String {
        var result = ""
        for (event in events.value!!) {
            result = result +  event + "\n\n"
        }
        return result
    }
}