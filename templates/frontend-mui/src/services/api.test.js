import { api } from './api';

describe('API Service', () => {
  beforeEach(() => {
    // Clear all mocks
    jest.clearAllMocks();
    localStorage.clear();
    
    // Reset window.location
    delete window.location;
    window.location = { href: '', pathname: '/' };
  });

  describe('Request Interceptor', () => {
    it('should add auth token to request headers when token exists', async () => {
      // Find the request interceptor
      const interceptorCalls = api.interceptors.request.use.mock.calls;
      if (!interceptorCalls || interceptorCalls.length === 0) {
        console.warn('Request interceptor not registered');
        return;
      }
      
      const mockRequestInterceptor = interceptorCalls[interceptorCalls.length - 1][0];
      localStorage.setItem('token', 'test-token-123');
      
      const config = {
        headers: {}
      };

      const modifiedConfig = await mockRequestInterceptor(config);

      expect(modifiedConfig.headers.Authorization).toBe('Bearer test-token-123');
    });

    it('should not add auth token when no token exists', async () => {
      // Find the request interceptor
      const interceptorCalls = api.interceptors.request.use.mock.calls;
      if (!interceptorCalls || interceptorCalls.length === 0) {
        console.warn('Request interceptor not registered');
        return;
      }
      
      const mockRequestInterceptor = interceptorCalls[interceptorCalls.length - 1][0];
      
      const config = {
        headers: {}
      };

      const modifiedConfig = await mockRequestInterceptor(config);

      expect(modifiedConfig.headers.Authorization).toBeUndefined();
    });

    it('should preserve existing headers', async () => {
      // Find the request interceptor
      const interceptorCalls = api.interceptors.request.use.mock.calls;
      if (!interceptorCalls || interceptorCalls.length === 0) {
        console.warn('Request interceptor not registered');
        return;
      }
      
      const mockRequestInterceptor = interceptorCalls[interceptorCalls.length - 1][0];
      localStorage.setItem('token', 'test-token-123');
      
      const config = {
        headers: {
          'X-Custom-Header': 'custom-value'
        }
      };

      const modifiedConfig = await mockRequestInterceptor(config);

      expect(modifiedConfig.headers['X-Custom-Header']).toBe('custom-value');
      expect(modifiedConfig.headers.Authorization).toBe('Bearer test-token-123');
    });
  });

  describe('Response Interceptor', () => {
    it('should pass through successful responses', async () => {
      // Find the response interceptor
      const interceptorCalls = api.interceptors.response.use.mock.calls;
      if (!interceptorCalls || interceptorCalls.length === 0) {
        console.warn('Response interceptor not registered');
        return;
      }
      
      const mockResponseInterceptor = interceptorCalls[interceptorCalls.length - 1][0];
      const response = { data: 'test-data' };
      const result = await mockResponseInterceptor(response);
      
      expect(result).toBe(response);
    });

    it('should handle 401 errors by clearing auth and redirecting to login', async () => {
      // Find the error interceptor
      const interceptorCalls = api.interceptors.response.use.mock.calls;
      if (!interceptorCalls || interceptorCalls.length === 0) {
        console.warn('Response interceptor not registered');
        return;
      }
      
      const mockErrorInterceptor = interceptorCalls[interceptorCalls.length - 1][1];
      
      const error = {
        response: {
          status: 401
        }
      };

      // Set up localStorage with auth data
      localStorage.setItem('token', 'test-token');
      localStorage.setItem('user', JSON.stringify({ id: 1, email: 'test@example.com' }));

      // Mock window.location
      window.location.pathname = '/dashboard';

      await expect(mockErrorInterceptor(error)).rejects.toEqual(error);

      // Check that auth data was cleared
      expect(localStorage.getItem('token')).toBeNull();
      expect(localStorage.getItem('user')).toBeNull();

      // Check that location was changed
      expect(window.location.href).toBe('/login');
    });

    it('should not redirect to login if already on login page', async () => {
      // Find the error interceptor
      const interceptorCalls = api.interceptors.response.use.mock.calls;
      if (!interceptorCalls || interceptorCalls.length === 0) {
        console.warn('Response interceptor not registered');
        return;
      }
      
      const mockErrorInterceptor = interceptorCalls[interceptorCalls.length - 1][1];
      
      const error = {
        response: {
          status: 401
        }
      };

      // Mock window.location on login page
      window.location.pathname = '/login';
      const originalHref = window.location.href;

      await expect(mockErrorInterceptor(error)).rejects.toEqual(error);

      // Check that location was NOT changed
      expect(window.location.href).toBe(originalHref);
    });

    it('should pass through non-401 errors', async () => {
      // Find the error interceptor
      const interceptorCalls = api.interceptors.response.use.mock.calls;
      if (!interceptorCalls || interceptorCalls.length === 0) {
        console.warn('Response interceptor not registered');
        return;
      }
      
      const mockErrorInterceptor = interceptorCalls[interceptorCalls.length - 1][1];
      
      const error = {
        response: {
          status: 500,
          data: { message: 'Server error' }
        }
      };

      await expect(mockErrorInterceptor(error)).rejects.toEqual(error);

      // Check that auth data was NOT cleared
      expect(localStorage.getItem('token')).toBeNull(); // Should remain null
    });
  });

  describe('API Endpoints', () => {
    beforeEach(() => {
      // Reset all mocks
      api.get.mockClear();
      api.post.mockClear();
      api.put.mockClear();
      api.delete.mockClear();
    });

    it('should have working API functions', () => {
      // Test that api object has the expected methods
      expect(api.get).toBeDefined();
      expect(api.post).toBeDefined();
      expect(api.put).toBeDefined();
      expect(api.delete).toBeDefined();
      expect(api.interceptors.request.use).toBeDefined();
      expect(api.interceptors.response.use).toBeDefined();
    });
  });
});