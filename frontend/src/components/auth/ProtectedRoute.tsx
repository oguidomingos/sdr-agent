import { Navigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAuth?: boolean;
}

export function ProtectedRoute({ children, requireAuth = true }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();

  console.log('ProtectedRoute:', { requireAuth, isAuthenticated, isLoading });

  // Show loading while checking auth status
  if (isLoading) {
    console.log('ProtectedRoute: Showing loading spinner');
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  // If this route requires authentication and user is not authenticated
  if (requireAuth && !isAuthenticated) {
    console.log('ProtectedRoute: Redirecting to login (need auth, not authenticated)');
    return <Navigate to="/login" replace />;
  }

  // If this route is for non-authenticated users (login/register) and user is authenticated
  if (!requireAuth && isAuthenticated) {
    console.log('ProtectedRoute: Redirecting to app (no auth needed, but authenticated)');
    return <Navigate to="/app" replace />;
  }

  console.log('ProtectedRoute: Rendering children');
  return <>{children}</>;
}