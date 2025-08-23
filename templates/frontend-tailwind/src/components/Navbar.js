import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Disclosure } from '@headlessui/react';
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';

function classNames(...classes) {
  return classes.filter(Boolean).join(' ');
}

export default function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  // Define navigation items based on authentication status
  const publicNavigation = [
    { name: 'Home', href: '/', current: false },
    { name: 'About', href: '/about', current: false },
  ];

  const authenticatedNavigation = [
    { name: 'Home', href: '/', current: false },
    { name: 'Users', href: '/users', current: false },
    { name: 'Items', href: '/items', current: false },
    { name: 'About', href: '/about', current: false },
    { name: 'My Account', href: '/my-account', current: false },
  ];

  const navigation = user ? authenticatedNavigation : publicNavigation;

  const updatedNavigation = navigation.map((item) => ({
    ...item,
    current: location.pathname === item.href,
  }));

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const handleSignIn = () => {
    navigate('/login');
  };

  const handleSignUp = () => {
    navigate('/register');
  };

  return (
    <Disclosure as="nav" className="bg-white shadow">
      {({ open }) => (
        <>
          <div className="mx-auto max-w-7xl px-2 sm:px-6 lg:px-8">
            <div className="relative flex h-16 items-center justify-between">
              <div className="absolute inset-y-0 left-0 flex items-center sm:hidden">
                <Disclosure.Button className="inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500">
                  <span className="sr-only">Open main menu</span>
                  {open ? (
                    <XMarkIcon className="block h-6 w-6" aria-hidden="true" />
                  ) : (
                    <Bars3Icon className="block h-6 w-6" aria-hidden="true" />
                  )}
                </Disclosure.Button>
              </div>
              
              <div className="flex flex-1 items-center justify-center sm:items-stretch sm:justify-start">
                <div className="flex flex-shrink-0 items-center">
                  <h1 className="text-xl font-bold text-gray-900">FullStack</h1>
                </div>
                <div className="hidden sm:ml-6 sm:block">
                  <div className="flex space-x-4">
                    {updatedNavigation.map((item) => (
                      <Link
                        key={item.name}
                        to={item.href}
                        className={classNames(
                          item.current
                            ? 'bg-blue-50 text-blue-700'
                            : 'text-gray-500 hover:bg-gray-100 hover:text-gray-700',
                          'rounded-md px-3 py-2 text-sm font-medium transition-colors duration-200'
                        )}
                        aria-current={item.current ? 'page' : undefined}
                      >
                        {item.name}
                      </Link>
                    ))}
                  </div>
                </div>
              </div>

              {/* Desktop Auth Buttons */}
              <div className="hidden sm:flex sm:items-center sm:space-x-2">
                {!user ? (
                  <>
                    <button
                      onClick={handleSignIn}
                      className="rounded-md px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 transition-colors duration-200"
                    >
                      Sign In
                    </button>
                    <button
                      onClick={handleSignUp}
                      className="rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors duration-200"
                    >
                      Sign Up
                    </button>
                  </>
                ) : (
                  <>
                    <span className="text-sm text-gray-700 mr-2">
                      {user.email}
                    </span>
                    <button
                      onClick={handleLogout}
                      className="rounded-md px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 transition-colors duration-200"
                    >
                      Logout
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>

          <Disclosure.Panel className="sm:hidden">
            <div className="space-y-1 px-2 pb-3 pt-2">
              {updatedNavigation.map((item) => (
                <Disclosure.Button
                  key={item.name}
                  as={Link}
                  to={item.href}
                  className={classNames(
                    item.current
                      ? 'bg-blue-50 text-blue-700'
                      : 'text-gray-500 hover:bg-gray-100 hover:text-gray-700',
                    'block rounded-md px-3 py-2 text-base font-medium transition-colors duration-200'
                  )}
                  aria-current={item.current ? 'page' : undefined}
                >
                  {item.name}
                </Disclosure.Button>
              ))}
              
              {/* Mobile Auth Buttons */}
              <div className="border-t border-gray-200 pt-3 mt-3">
                {!user ? (
                  <>
                    <Disclosure.Button
                      as="button"
                      onClick={handleSignIn}
                      className="block w-full text-left rounded-md px-3 py-2 text-base font-medium text-gray-700 hover:bg-gray-100 transition-colors duration-200"
                    >
                      Sign In
                    </Disclosure.Button>
                    <Disclosure.Button
                      as="button"
                      onClick={handleSignUp}
                      className="block w-full text-left rounded-md px-3 py-2 text-base font-medium text-gray-700 hover:bg-gray-100 transition-colors duration-200 mt-1"
                    >
                      Sign Up
                    </Disclosure.Button>
                  </>
                ) : (
                  <>
                    <div className="px-3 py-2 text-sm text-gray-700">
                      {user.email}
                    </div>
                    <Disclosure.Button
                      as="button"
                      onClick={handleLogout}
                      className="block w-full text-left rounded-md px-3 py-2 text-base font-medium text-gray-700 hover:bg-gray-100 transition-colors duration-200"
                    >
                      Logout
                    </Disclosure.Button>
                  </>
                )}
              </div>
            </div>
          </Disclosure.Panel>
        </>
      )}
    </Disclosure>
  );
}