import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';
import '@mantine/dates/styles.css';
import '@mantine/charts/styles.css';

import { MantineProvider } from '@mantine/core';
import { Notifications } from '@mantine/notifications';
import { Router } from './Router';
import { theme } from './theme';

// Global styles for animations
import './styles.css';

export default function App() {
  return (
    <MantineProvider theme={theme}>
      <Notifications />
      <Router />
    </MantineProvider>
  );
}
