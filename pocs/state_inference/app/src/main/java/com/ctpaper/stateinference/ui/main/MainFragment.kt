package com.ctpaper.stateinference.ui.main

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.webkit.URLUtil
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import com.ctpaper.stateinference.AttackHandler
import com.ctpaper.stateinference.databinding.MainFragmentBinding
import com.ctpaper.stateinference.ui.OverlayActivity
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainFragment : Fragment() {

    companion object {
        fun newInstance() = MainFragment()
    }

    private lateinit var binding: MainFragmentBinding
    private lateinit var viewModel: MainViewModel

    private lateinit var attackHandler: AttackHandler

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        binding = MainFragmentBinding.inflate(layoutInflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        viewModel = ViewModelProvider(this).get(MainViewModel::class.java)

        viewModel.start()

        attackHandler =
            AttackHandler(requireActivity(), viewModel, binding.webview)

        binding.launchCustomTabButton.setOnClickListener {
            val intent = Intent(requireActivity(), OverlayActivity::class.java)
            viewModel.url.value = binding.url.text.toString()
            if (URLUtil.isValidUrl(viewModel.url.value)){
                attackHandler.navigate(intent)
            } else {
                Toast.makeText(requireActivity(), "Enter a valid URL", Toast.LENGTH_SHORT).show()
            }
        }

        viewModel.events.observe(viewLifecycleOwner, {
            binding.textView.text = viewModel.formatEvents()
        })
    }
}