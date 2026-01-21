import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Formik, Form, Field, FormikHelpers } from 'formik';
import * as Yup from 'yup';
import { useAuth } from '../../hooks/useAuth';
import { authMessages } from './messages';
import { ApiError } from '../../services/api';
import './styles.scss';

interface RegisterFormValues {
  email: string;
  password: string;
  confirmPassword: string;
  first_name: string;
  last_name: string;
}

const validationSchema = Yup.object({
  email: Yup.string()
    .email(authMessages.validation.emailInvalid)
    .required(authMessages.validation.emailRequired),
  password: Yup.string()
    .min(8, authMessages.validation.passwordMinLength)
    .required(authMessages.validation.passwordRequired),
  confirmPassword: Yup.string()
    .oneOf([Yup.ref('password')], authMessages.validation.passwordsNotMatch)
    .required(authMessages.validation.passwordRequired),
  first_name: Yup.string()
    .required(authMessages.validation.firstNameRequired),
  last_name: Yup.string()
    .required(authMessages.validation.lastNameRequired),
});

const initialValues: RegisterFormValues = {
  email: '',
  password: '',
  confirmPassword: '',
  first_name: '',
  last_name: '',
};

const Register: React.FC = () => {
  const navigate = useNavigate();
  const { register, isAuthenticated } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Redirect if already authenticated
  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/orders', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (
    values: RegisterFormValues,
    { setSubmitting }: FormikHelpers<RegisterFormValues>
  ) => {
    setError(null);
    setSuccess(null);
    
    try {
      await register({
        email: values.email,
        password: values.password,
        first_name: values.first_name,
        last_name: values.last_name,
      });
      setSuccess(authMessages.register.successMessage);
      // Redirect to login after 2 seconds
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err) {
      if (err instanceof ApiError && err.status === 400) {
        setError(authMessages.register.errorEmailExists);
      } else {
        setError(authMessages.register.errorGeneric);
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container register">
        <div className="auth-header">
          <h1 className="auth-title">{authMessages.register.title}</h1>
          <p className="auth-subtitle">{authMessages.register.subtitle}</p>
        </div>

        {error && (
          <div className="auth-alert error">{error}</div>
        )}

        {success && (
          <div className="auth-alert success">{success}</div>
        )}

        <Formik
          initialValues={initialValues}
          validationSchema={validationSchema}
          onSubmit={handleSubmit}
        >
          {({ errors, touched, isSubmitting }) => (
            <Form className="auth-form">
              <div className="form-row">
                <div className="form-field">
                  <label htmlFor="first_name">{authMessages.register.firstNameLabel}</label>
                  <Field
                    id="first_name"
                    name="first_name"
                    type="text"
                    placeholder={authMessages.register.firstNamePlaceholder}
                    className={errors.first_name && touched.first_name ? 'error' : ''}
                  />
                  {errors.first_name && touched.first_name && (
                    <span className="field-error">{errors.first_name}</span>
                  )}
                </div>

                <div className="form-field">
                  <label htmlFor="last_name">{authMessages.register.lastNameLabel}</label>
                  <Field
                    id="last_name"
                    name="last_name"
                    type="text"
                    placeholder={authMessages.register.lastNamePlaceholder}
                    className={errors.last_name && touched.last_name ? 'error' : ''}
                  />
                  {errors.last_name && touched.last_name && (
                    <span className="field-error">{errors.last_name}</span>
                  )}
                </div>
              </div>

              <div className="form-field">
                <label htmlFor="email">{authMessages.register.emailLabel}</label>
                <Field
                  id="email"
                  name="email"
                  type="email"
                  placeholder={authMessages.register.emailPlaceholder}
                  className={errors.email && touched.email ? 'error' : ''}
                />
                {errors.email && touched.email && (
                  <span className="field-error">{errors.email}</span>
                )}
              </div>

              <div className="form-field">
                <label htmlFor="password">{authMessages.register.passwordLabel}</label>
                <Field
                  id="password"
                  name="password"
                  type="password"
                  placeholder={authMessages.register.passwordPlaceholder}
                  className={errors.password && touched.password ? 'error' : ''}
                />
                {errors.password && touched.password && (
                  <span className="field-error">{errors.password}</span>
                )}
              </div>

              <div className="form-field">
                <label htmlFor="confirmPassword">{authMessages.register.confirmPasswordLabel}</label>
                <Field
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  placeholder={authMessages.register.confirmPasswordPlaceholder}
                  className={errors.confirmPassword && touched.confirmPassword ? 'error' : ''}
                />
                {errors.confirmPassword && touched.confirmPassword && (
                  <span className="field-error">{errors.confirmPassword}</span>
                )}
              </div>

              <button
                type="submit"
                className="auth-submit-button"
                disabled={isSubmitting}
              >
                {isSubmitting ? '...' : authMessages.register.submitButton}
              </button>
            </Form>
          )}
        </Formik>

        <div className="auth-footer">
          <p className="auth-footer-text">
            {authMessages.register.hasAccount}{' '}
            <Link to="/login">{authMessages.register.loginLink}</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
