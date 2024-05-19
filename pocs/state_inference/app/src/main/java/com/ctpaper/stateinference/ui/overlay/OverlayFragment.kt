package com.ctpaper.stateinference.ui.overlay

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import com.ctpaper.stateinference.databinding.OverlayFragmentBinding
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class OverlayFragment : Fragment() {

    companion object {
        fun newInstance() = OverlayFragment()
    }

    private lateinit var binding: OverlayFragmentBinding
    private lateinit var viewModel: OverlayViewModel


    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        binding = OverlayFragmentBinding.inflate(layoutInflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        viewModel = ViewModelProvider(this).get(OverlayViewModel::class.java)
    }
}