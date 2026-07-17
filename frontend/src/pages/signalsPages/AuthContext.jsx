import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
	const context = useContext(AuthContext);
	if (!context) {
		throw new Error('useAuth must be used within AuthProvider');
	}
	return context;
};

export const AuthProvider = ({ children }) => {
	const [isAuthenticated, setIsAuthenticated] = useState(false);
	const [apiKey, setApiKey] = useState(null);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		const savedKey = localStorage.getItem('adminApiKey');
		if (savedKey) {
			setApiKey(savedKey);
			setIsAuthenticated(true);
		}
		setLoading(false);
	}, []);

	const login = (key) => {
		setApiKey(key);
		setIsAuthenticated(true);
		localStorage.setItem('adminApiKey', key);
		axios.defaults.headers.common['X-API-Key'] = key;
	};

	const logout = () => {
		setApiKey(null);
		setIsAuthenticated(false);
		localStorage.removeItem('adminApiKey');
		delete axios.defaults.headers.common['X-API-Key'];
	};

	const value = {
		isAuthenticated,
		apiKey,
		login,
		logout,
		loading
	};

	return (
		<AuthContext.Provider value={value}>
			{children}
		</AuthContext.Provider>
	);
};