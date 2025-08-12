import React, { useState } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { AlertCircle, Eye, EyeOff, Mail, Lock, LogIn } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const LoginForm = ({ onSwitchToRegister }) => {
  const { login } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.email) {
      newErrors.email = 'Email requis';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email invalide';
    }

    if (!formData.password) {
      newErrors.password = 'Mot de passe requis';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setLoading(true);
    setErrors({});

    try {
      const result = await login(formData.email, formData.password);
      
      if (!result.success) {
        setErrors({ general: result.message });
      }
      // On success, the AuthContext will handle the redirect
    } catch (error) {
      setErrors({ general: 'Erreur de connexion. Veuillez réessayer.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-md mx-auto bg-gray-800/90 border-gray-700 backdrop-blur-sm">
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl text-center text-white">
          <LogIn className="w-6 h-6 mx-auto mb-2 text-blue-400" />
          Connexion
        </CardTitle>
        <CardDescription className="text-center text-gray-400">
          Connectez-vous à votre compte ForexPro
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {errors.general && (
            <div className="flex items-center gap-2 p-3 bg-red-900/50 border border-red-700 rounded-lg text-red-300">
              <AlertCircle className="w-4 h-4" />
              <span className="text-sm">{errors.general}</span>
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="email" className="text-white">
              <Mail className="w-4 h-4 inline mr-2" />
              Email
            </Label>
            <Input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="votre@email.com"
              className="bg-gray-700 border-gray-600 text-white placeholder-gray-400"
              disabled={loading}
            />
            {errors.email && (
              <p className="text-red-400 text-sm">{errors.email}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="password" className="text-white">
              <Lock className="w-4 h-4 inline mr-2" />
              Mot de passe
            </Label>
            <div className="relative">
              <Input
                id="password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                className="bg-gray-700 border-gray-600 text-white placeholder-gray-400 pr-10"
                disabled={loading}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
                disabled={loading}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {errors.password && (
              <p className="text-red-400 text-sm">{errors.password}</p>
            )}
          </div>

          <Button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white"
            disabled={loading}
          >
            {loading ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Connexion...
              </div>
            ) : (
              'Se connecter'
            )}
          </Button>

          <div className="text-center pt-4">
            <p className="text-gray-400 text-sm">
              Pas encore de compte ?{' '}
              <button
                type="button"
                onClick={onSwitchToRegister}
                className="text-blue-400 hover:text-blue-300 underline"
                disabled={loading}
              >
                S'inscrire
              </button>
            </p>
          </div>
        </form>
      </CardContent>
    </Card>
  );
};

export default LoginForm;