import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Formik, Form, Field, FormikHelpers } from 'formik';
import * as Yup from 'yup';
import { useAuth } from '../../hooks/useAuth';
import { UserLogin } from '../../types';
import { authMessages } from './messages';
import { ApiError } from '../../services/api';
import './styles.scss';

const validationSchema = Yup.object({
  email: Yup.string()
    .email(authMessages.validation.emailInvalid)
    .required(authMessages.validation.emailRequired),
  password: Yup.string()
    .required(authMessages.validation.passwordRequired),
});

const initialValues: UserLogin = {
  email: '',
  password: '',
};

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login, isAuthenticated } = useAuth();
  const [error, setError] = useState<string | null>(null);

  // Redirect if already authenticated
  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/orders', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (
    values: UserLogin,
    { setSubmitting }: FormikHelpers<UserLogin>
  ) => {
    setError(null);
    try {
      await login(values);
      navigate('/orders', { replace: true });
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setError(authMessages.login.errorInvalidCredentials);
      } else {
        setError(authMessages.login.errorGeneric);
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <h1 className="auth-title">{authMessages.login.title}</h1>
          <p className="auth-subtitle">{authMessages.login.subtitle}</p>
        </div>

        {error && (
          <div className="auth-alert error">{error}</div>
        )}

        <Formik
          initialValues={initialValues}
          validationSchema={validationSchema}
          onSubmit={handleSubmit}
        >
          {({ errors, touched, isSubmitting }) => (
            <Form className="auth-form">
              <div className="form-field">
                <label htmlFor="email">{authMessages.login.emailLabel}</label>
                <Field
                  id="email"
                  name="email"
                  type="email"
                  placeholder={authMessages.login.emailPlaceholder}
                  className={errors.email && touched.email ? 'error' : ''}
                />
                {errors.email && touched.email && (
                  <span className="field-error">{errors.email}</span>
                )}
              </div>

              <div className="form-field">
                <label htmlFor="password">{authMessages.login.passwordLabel}</label>
                <Field
                  id="password"
                  name="password"
                  type="password"
                  placeholder={authMessages.login.passwordPlaceholder}
                  className={errors.password && touched.password ? 'error' : ''}
                />
                {errors.password && touched.password && (
                  <span className="field-error">{errors.password}</span>
                )}
              </div>

              <button
                type="submit"
                className="auth-submit-button"
                disabled={isSubmitting}
              >
                {isSubmitting ? '...' : authMessages.login.submitButton}
              </button>
            </Form>
          )}
        </Formik>

        <div className="auth-footer">
          <p className="auth-footer-text">
            {authMessages.login.noAccount}{' '}
            <Link to="/register">{authMessages.login.registerLink}</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
