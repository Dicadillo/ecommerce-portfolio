import { Link, Outlet } from 'react-router-dom';

import { MainNavigation } from '../components/MainNavigation';

export function MainLayout() {
  return (
    <div className="app-shell">
      <header className="site-header">
        <Link className="brand" to="/">
          Ecommerce QA
        </Link>
        <MainNavigation />
      </header>

      <main className="page-content">
        <Outlet />
      </main>

      <footer className="site-footer">
        <p>Portfolio de automatización de pruebas</p>
      </footer>
    </div>
  );
}
