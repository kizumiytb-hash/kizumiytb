import React, { useState } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { AlertCircle, Eye, EyeOff, Mail, Lock, User, Phone, UserPlus, CheckCircle } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const RegisterForm = ({ onSwitchToLogin }) => {
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
    phone: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
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
    } else if (formData.password.length < 6) {
      newErrors.password = 'Le mot de passe doit contenir au moins 6 caractères';
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Confirmation du mot de passe requise';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Les mots de passe ne correspondent pas';
    }

    if (!formData.first_name.trim()) {
      newErrors.first_name = 'Prénom requis';
    }

    if (!formData.last_name.trim()) {
      newErrors.last_name = 'Nom requis';
    }

    if (formData.phone && !/^[\d\s\-\+\(\)]+$/.test(formData.phone)) {
      newErrors.phone = 'Format de téléphone invalide';
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
      const result = await register({
        email: formData.email,
        password: formData.password,
        first_name: formData.first_name.trim(),
        last_name: formData.last_name.trim(),
        phone: formData.phone.trim() || null
      });
      
      if (!result.success) {
        setErrors({ general: result.message });
      }
      // On success, the AuthContext will handle the redirect
    } catch (error) {
      setErrors({ general: 'Erreur d\'inscription. Veuillez réessayer.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-md mx-auto bg-gray-800/90 border-gray-700 backdrop-blur-sm">
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl text-center text-white">
          <UserPlus className="w-6 h-6 mx-auto mb-2 text-green-400" />
          Inscription
        </CardTitle>
        <CardDescription className="text-center text-gray-400">
          Créez votre compte ForexPro
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

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-2">
              <Label htmlFor="first_name" className="text-white">
                <User className="w-4 h-4 inline mr-2" />
                Prénom
              </Label>
              <Input
                id="first_name"
                name="first_name"
                type="text"
                value={formData.first_name}
                onChange={handleChange}
                placeholder="Jean"
                className="bg-gray-700 border-gray-600 text-white placeholder-gray-400"
                disabled={loading}
              />
              {errors.first_name && (
                <p className="text-red-400 text-sm">{errors.first_name}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="last_name" className="text-white">
                Nom
              </Label>
              <Input
                id="last_name"
                name="last_name"
                type="text"
                value={formData.last_name}
                onChange={handleChange}
                placeholder="Dupont"
                className="bg-gray-700 border-gray-600 text-white placeholder-gray-400"
                disabled={loading}
              />
              {errors.last_name && (
                <p className="text-red-400 text-sm">{errors.last_name}</p>
              )}
            </div>
          </div>

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
            <Label htmlFor="phone" className="text-white">
              <Phone className="w-4 h-4 inline mr-2" />
              Téléphone (optionnel)
            </Label>
            <Input
              id="phone"
              name="phone"
              type="tel"
              value={formData.phone}
              onChange={handleChange}
              placeholder="+33 1 23 45 67 89"
              className="bg-gray-700 border-gray-600 text-white placeholder-gray-400"
              disabled={loading}
            />
            {errors.phone && (
              <p className="text-red-400 text-sm">{errors.phone}</p>
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

          <div className="space-y-2">
            <Label htmlFor="confirmPassword" className="text-white">
              <Lock className="w-4 h-4 inline mr-2" />
              Confirmer le mot de passe
            </Label>
            <div className="relative">
              <Input
                id="confirmPassword"
                name="confirmPassword"
                type={showConfirmPassword ? 'text' : 'password'}
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="••••••••"
                className="bg-gray-700 border-gray-600 text-white placeholder-gray-400 pr-10"
                disabled={loading}
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
                disabled={loading}
              >
                {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {errors.confirmPassword && (
              <p className="text-red-400 text-sm">{errors.confirmPassword}</p>
            )}
          </div>

          <Button
            type="submit"
            className="w-full bg-green-600 hover:bg-green-700 text-white"
            disabled={loading}
          >
            {loading ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Inscription...
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4" />
                Créer mon compte
              </div>
            )}
          </Button>

          <div className="text-center pt-4">
            <p className="text-gray-400 text-sm">
              Déjà un compte ?{' '}
              <button
                type="button"
                onClick={onSwitchToLogin}
                className="text-blue-400 hover:text-blue-300 underline"
                disabled={loading}
              >
                Se connecter
              </button>
            </p>
          </div>
        </form>
      </CardContent>
    </Card>
  );
};

export default RegisterForm;