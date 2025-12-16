import { createTheme } from '@mantine/core';

export const theme = createTheme({
  /** Customize dark mode colors for better contrast and eye comfort */
  colors: {
    dark: [
      '#C1C2C5', // text
      '#A6A7AB', // dimmed text
      '#909296', // hover
      '#5c5f66', // border
      '#373A40', // input
      '#2C2E33', // card background (not too dark)
      '#25262b', // body background (accessible dark)
      '#1A1B1E', // darker background
      '#141517', // darkest
      '#101113', // almost black
    ],
  },
  /** Ensure good contrast in dark mode */
  primaryColor: 'violet',
});



