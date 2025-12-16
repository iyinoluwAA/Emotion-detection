import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { HomePage } from './pages/Home.page';
import { LandingPage } from './pages/Landing.page';

const router = createBrowserRouter([
  {
    path: '/',
    element: <LandingPage />,
  },
  {
    path: '/app',
    element: <HomePage />,
  },
]);

export function Router() {
  return <RouterProvider router={router} />;
}
