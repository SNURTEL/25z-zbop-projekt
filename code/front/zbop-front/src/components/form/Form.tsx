import React from 'react';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import { messages } from './messages';
import './styles.scss';
import { submitFormData } from './utils';

export type FormValues = {
  maxCoffeeMagazineCapacity: number | '';
  conferencesPerWeek: number | '';
  normalWorkersDaily: number | '';
};

export type FormProps = {
  onSubmit?: (values: FormValues) => Promise<void>;
};

const validationSchema = Yup.object({
  maxCoffeeMagazineCapacity: Yup.number()
    .typeError(messages.validation.number)
    .integer(messages.validation.integer)
    .min(0, messages.validation.nonNegative)
    .required(messages.validation.required),
  conferencesPerWeek: Yup.number()
    .typeError(messages.validation.number)
    .integer(messages.validation.integer)
    .min(0, messages.validation.nonNegative)
    .required(messages.validation.required),
  normalWorkersDaily: Yup.number()
    .typeError(messages.validation.number)
    .integer(messages.validation.integer)
    .min(0, messages.validation.nonNegative)
    .required(messages.validation.required),
});

const initialValues: FormValues = {
  maxCoffeeMagazineCapacity: '',
  conferencesPerWeek: '',
  normalWorkersDaily: '',
};

const FormPage: React.FC<FormProps> = ({ onSubmit }) => {
  const handleSubmit = async (values: FormValues, { setSubmitting, resetForm }: any) => {
    try {
      if (onSubmit) {
        await onSubmit(values);
      } else {
        await submitFormData({
          maxCoffeeMagazineCapacity: Number(values.maxCoffeeMagazineCapacity),
          conferencesPerWeek: Number(values.conferencesPerWeek),
          normalWorkersDaily: Number(values.normalWorkersDaily),
        });
        resetForm();
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box className="form-page">
      <Formik initialValues={initialValues} validationSchema={validationSchema} onSubmit={handleSubmit}>
        {({ isSubmitting }) => (
          <Form>
            <Stack spacing={3}>
              <Field name="maxCoffeeMagazineCapacity">
                {({ field, meta }: any) => (
                  <TextField
                    {...field}
                    type="number"
                    label={messages.fields.maxCoffeeMagazineCapacity}
                    fullWidth
                    slotProps={{ input: { min: 0 } }}
                    error={meta.touched && Boolean(meta.error)}
                    helperText={meta.touched && meta.error}
                  />
                )}
              </Field>
              <Field name="conferencesPerWeek">
                {({ field, meta }: any) => (
                  <TextField
                    {...field}
                    type="number"
                    label={messages.fields.conferencesPerWeek}
                    fullWidth
                    slotProps={{ input: { min: 0 } }}
                    error={meta.touched && Boolean(meta.error)}
                    helperText={meta.touched && meta.error}
                  />
                )}
              </Field>
              <Field name="normalWorkersDaily">
                {({ field, meta }: any) => (
                  <TextField
                    {...field}
                    type="number"
                    label={messages.fields.normalWorkersDaily}
                    fullWidth
                    slotProps={{ input: { min: 0 } }}
                    error={meta.touched && Boolean(meta.error)}
                    helperText={meta.touched && meta.error}
                  />
                )}
              </Field>

              <Box display="flex" justifyContent="flex-end" gap={2}>
                <Button type="reset" variant="outlined" disabled={isSubmitting}>
                  {messages.actions.reset}
                </Button>
                <Button type="submit" variant="contained" disabled={isSubmitting}>
                  {messages.actions.submit}
                </Button>
              </Box>
            </Stack>
          </Form>
        )}
      </Formik>
    </Box>
  );
};

export default FormPage;


