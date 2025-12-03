import React from 'react'
import ReactDOM from 'react-dom/client'
import '@fontsource-variable/raleway'
import { ChakraProvider, extendTheme, type ThemeConfig } from '@chakra-ui/react'
import App from './App.tsx'
import './index.css'

// Configure dark mode as default
const config: ThemeConfig = {
  initialColorMode: 'dark',
  useSystemColorMode: false,
}

const theme = extendTheme({ 
  config,
  fonts: {
    heading: `'Raleway Variable', sans-serif`,
    body: `'Raleway Variable', sans-serif`,
  },
  styles: {
    global: {
      body: {
        bg: "#0f0f12",       // darker, neutral background
        color: "gray.200",
      },
    },
  },
  colors: {
    gray: {
      800: "#141418",       // darker-gray overrides
      900: "#0f0f12",
      700: "#1b1b1f",
      600: "#2a2a30",
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ChakraProvider theme={theme}>
      <App />
    </ChakraProvider>
  </React.StrictMode>,
)
