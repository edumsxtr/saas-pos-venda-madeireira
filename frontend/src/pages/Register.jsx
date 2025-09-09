import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Eye, EyeOff } from 'lucide-react';
import { authAPI } from '@/lib/api';
import { useAuth, useNotifications } from '@/lib/store';

const registerSchema = z.object({
  nome: z.string().min(2, 'Nome deve ter pelo menos 2 caracteres'),
  email: z.string().email('Email inválido'),
  password: z.string().min(6, 'Senha deve ter pelo menos 6 caracteres'),
  confirmPassword: z.string(),
  empresa_nome: z.string().min(2, 'Nome da empresa deve ter pelo menos 2 caracteres'),
  empresa_slug: z.string()
    .min(2, 'Slug deve ter pelo menos 2 caracteres')
    .regex(/^[a-z0-9-]+$/, 'Slug deve conter apenas letras minúsculas, números e hífens'),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Senhas não coincidem",
  path: ["confirmPassword"],
});

export default function Register() {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  const navigate = useNavigate();
  const { login } = useAuth();
  const { showSuccess } = useNotifications();

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(registerSchema),
  });

  const empresaNome = watch('empresa_nome');

  // Gerar slug automaticamente baseado no nome da empresa
  const generateSlug = (nome) => {
    if (!nome) return '';
    return nome
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '') // Remove acentos
      .replace(/[^a-z0-9\s-]/g, '') // Remove caracteres especiais
      .replace(/\s+/g, '-') // Substitui espaços por hífens
      .replace(/-+/g, '-') // Remove hífens duplicados
      .trim();
  };

  // Atualizar slug quando o nome da empresa mudar
  React.useEffect(() => {
    if (empresaNome) {
      setValue('empresa_slug', generateSlug(empresaNome));
    }
  }, [empresaNome, setValue]);

  const onSubmit = async (data) => {
    setIsLoading(true);
    setError('');

    try {
      const response = await authAPI.register(
        data.nome,
        data.email,
        data.password,
        data.empresa_nome,
        data.empresa_slug
      );
      
      const { user, tokens } = response.data;
      
      login(user, tokens);
      showSuccess('Conta criada com sucesso!');
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.message || 'Erro ao criar conta');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Crie sua conta
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            SaaS Pós-Venda - Madeireira Cambará
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Registrar</CardTitle>
            <CardDescription>
              Preencha os dados para criar sua conta e empresa
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {/* Dados pessoais */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Dados pessoais</h3>
                
                <div className="space-y-2">
                  <Label htmlFor="nome">Nome completo</Label>
                  <Input
                    id="nome"
                    type="text"
                    placeholder="Seu nome completo"
                    {...register('nome')}
                    className={errors.nome ? 'border-red-500' : ''}
                  />
                  {errors.nome && (
                    <p className="text-sm text-red-500">{errors.nome.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="seu@email.com"
                    {...register('email')}
                    className={errors.email ? 'border-red-500' : ''}
                  />
                  {errors.email && (
                    <p className="text-sm text-red-500">{errors.email.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password">Senha</Label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="Mínimo 6 caracteres"
                      {...register('password')}
                      className={errors.password ? 'border-red-500' : ''}
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                  {errors.password && (
                    <p className="text-sm text-red-500">{errors.password.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirmar senha</Label>
                  <div className="relative">
                    <Input
                      id="confirmPassword"
                      type={showConfirmPassword ? 'text' : 'password'}
                      placeholder="Confirme sua senha"
                      {...register('confirmPassword')}
                      className={errors.confirmPassword ? 'border-red-500' : ''}
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    >
                      {showConfirmPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                  {errors.confirmPassword && (
                    <p className="text-sm text-red-500">{errors.confirmPassword.message}</p>
                  )}
                </div>
              </div>

              {/* Dados da empresa */}
              <div className="space-y-4 pt-4 border-t">
                <h3 className="text-lg font-medium">Dados da empresa</h3>
                
                <div className="space-y-2">
                  <Label htmlFor="empresa_nome">Nome da empresa</Label>
                  <Input
                    id="empresa_nome"
                    type="text"
                    placeholder="Nome da sua empresa"
                    {...register('empresa_nome')}
                    className={errors.empresa_nome ? 'border-red-500' : ''}
                  />
                  {errors.empresa_nome && (
                    <p className="text-sm text-red-500">{errors.empresa_nome.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="empresa_slug">Identificador da empresa</Label>
                  <Input
                    id="empresa_slug"
                    type="text"
                    placeholder="identificador-da-empresa"
                    {...register('empresa_slug')}
                    className={errors.empresa_slug ? 'border-red-500' : ''}
                  />
                  <p className="text-xs text-gray-500">
                    Este será usado na URL da sua empresa. Apenas letras minúsculas, números e hífens.
                  </p>
                  {errors.empresa_slug && (
                    <p className="text-sm text-red-500">{errors.empresa_slug.message}</p>
                  )}
                </div>
              </div>

              <Button
                type="submit"
                className="w-full"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Criando conta...
                  </>
                ) : (
                  'Criar conta'
                )}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                Já tem uma conta?{' '}
                <Link
                  to="/login"
                  className="font-medium text-blue-600 hover:text-blue-500"
                >
                  Faça login aqui
                </Link>
              </p>
            </div>
          </CardContent>
        </Card>

        <div className="text-center">
          <p className="text-xs text-gray-500">
            © 2024 SaaS Pós-Venda. Todos os direitos reservados.
          </p>
        </div>
      </div>
    </div>
  );
}

