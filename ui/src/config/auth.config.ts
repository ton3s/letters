/**
 * Authentication configuration
 * Controls whether authentication is required for the application
 */

// Set to true to require authentication for all routes
// Set to false to make authentication optional
export const REQUIRE_AUTH = process.env.REACT_APP_REQUIRE_AUTH === 'true' || false;

// You can also configure per-route authentication requirements
export const ROUTE_AUTH_CONFIG = {
  '/generate': REQUIRE_AUTH,
  '/history': REQUIRE_AUTH,
  '/letter/view': REQUIRE_AUTH,
  '/settings': REQUIRE_AUTH,
};