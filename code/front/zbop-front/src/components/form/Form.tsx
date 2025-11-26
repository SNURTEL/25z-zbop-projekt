import React, { useState } from 'react';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Slider from '@mui/material/Slider';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Grid from '@mui/material/Grid';
import { messages } from './messages';
import './styles.scss';
import { submitFormData } from './utils';

export type FormValues = {
  planningHorizonDays: number;
  numConferencesDaily: number[];
  numWorkersDaily: number[];
  purchaseCostsDaily: number[];
  storageCapacityKg: number | '';
  transportCostPln: number | '';
  initialInventoryKg: number | '';
  dailyLossFraction: number | '';
};

export type FormProps = {
  onSubmit?: (values: FormValues) => Promise<void>;
};

const validationSchema = Yup.object({
  planningHorizonDays: Yup.number()
    .typeError(messages.validation.number)
    .integer(messages.validation.integer)
    .min(1, messages.validation.positive)
    .max(31, 'Maximum 31 days')
    .required(messages.validation.required),
  numConferencesDaily: Yup.array()
    .of(Yup.number().min(0, messages.validation.nonNegative).integer(messages.validation.integer))
    .required(messages.validation.required),
  numWorkersDaily: Yup.array()
    .of(Yup.number().min(0, messages.validation.nonNegative).integer(messages.validation.integer))
    .required(messages.validation.required),
  purchaseCostsDaily: Yup.array()
    .of(Yup.number().min(1, messages.validation.positive).integer(messages.validation.integer))
    .required(messages.validation.required),
  storageCapacityKg: Yup.number()
    .typeError(messages.validation.number)
    .integer(messages.validation.integer)
    .min(1, messages.validation.positive)
    .required(messages.validation.required),
  transportCostPln: Yup.number()
    .typeError(messages.validation.number)
    .min(0, messages.validation.nonNegative)
    .required(messages.validation.required),
  initialInventoryKg: Yup.number()
    .typeError(messages.validation.number)
    .min(0, messages.validation.nonNegative)
    .required(messages.validation.required),
  dailyLossFraction: Yup.number()
    .typeError(messages.validation.number)
    .min(0, messages.validation.between0and1)
    .max(1, messages.validation.between0and1)
    .required(messages.validation.required),
});

const initialValues: FormValues = {
  planningHorizonDays: 7,
  numConferencesDaily: Array(7).fill(1),
  numWorkersDaily: Array(7).fill(20),
  purchaseCostsDaily: Array(7).fill(12),
  storageCapacityKg: 150,
  transportCostPln: 100,
  initialInventoryKg: 40,
  dailyLossFraction: 0.1,
};

// Helper component to handle array resizing with proper hook usage
const FormContent: React.FC<{
  isSubmitting: boolean;
  values: FormValues;
  setFieldValue: (field: string, value: any) => void;
  fillConferencesValue: string;
  setFillConferencesValue: (value: string) => void;
  fillWorkersValue: string;
  setFillWorkersValue: (value: string) => void;
  fillCostsValue: string;
  setFillCostsValue: (value: string) => void;
}> = ({
  isSubmitting,
  values,
  setFieldValue,
  fillConferencesValue,
  setFillConferencesValue,
  fillWorkersValue,
  setFillWorkersValue,
  fillCostsValue,
  setFillCostsValue,
}) => {
  const [isAdvancedExpanded, setIsAdvancedExpanded] = useState(false);

  // Update arrays when planning horizon changes
  React.useEffect(() => {
    const currentLength = values.numConferencesDaily.length;
    if (values.planningHorizonDays !== currentLength) {
      if (values.planningHorizonDays > currentLength) {
        setFieldValue('numConferencesDaily', [...values.numConferencesDaily, ...Array(values.planningHorizonDays - currentLength).fill(1)]);
        setFieldValue('numWorkersDaily', [...values.numWorkersDaily, ...Array(values.planningHorizonDays - currentLength).fill(20)]);
        setFieldValue('purchaseCostsDaily', [...values.purchaseCostsDaily, ...Array(values.planningHorizonDays - currentLength).fill(12)]);
      } else {
        setFieldValue('numConferencesDaily', values.numConferencesDaily.slice(0, values.planningHorizonDays));
        setFieldValue('numWorkersDaily', values.numWorkersDaily.slice(0, values.planningHorizonDays));
        setFieldValue('purchaseCostsDaily', values.purchaseCostsDaily.slice(0, values.planningHorizonDays));
      }
    }
  }, [values.planningHorizonDays, values.numConferencesDaily.length, setFieldValue]);

  return (
            <Form>
              <Stack spacing={4}>
                <Box>
                  <Typography gutterBottom>
                    {messages.fields.planningHorizonDays}: {values.planningHorizonDays}
                  </Typography>
                  <Slider
                    value={values.planningHorizonDays}
                    onChange={(_, value) => setFieldValue('planningHorizonDays', value)}
                    min={1}
                    max={31}
                    marks
                    valueLabelDisplay="auto"
                  />
                </Box>

                <Grid container spacing={2}>
                  <Grid size={{ xs: 12, md: 4 }}>
                    <Box>
                      <Typography variant="h6" gutterBottom>
                        {messages.fields.numConferencesDaily}
                      </Typography>
                  <Stack spacing={2}>
                    <Box display="flex" gap={2} alignItems="center">
                      <TextField
                        type="number"
                        label={messages.fields.fillAllConferences}
                        value={fillConferencesValue}
                        onChange={(e) => setFillConferencesValue(e.target.value)}
                        InputProps={{ inputProps: { min: 0, step: 1 } }}
                        size="small"
                        sx={{ flex: 1 }}
                      />
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => {
                          const val = parseInt(fillConferencesValue) || 0;
                          setFieldValue('numConferencesDaily', Array(values.planningHorizonDays).fill(val));
                        }}
                        sx={{ minWidth: '100px' }}
                      >
                        Fill All
                      </Button>
                    </Box>
                    <TableContainer component={Paper}>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell><strong>Day</strong></TableCell>
                            <TableCell align="right"><strong>Conferences</strong></TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {values.numConferencesDaily.map((val, idx) => (
                            <TableRow key={idx}>
                              <TableCell>Day {idx + 1}</TableCell>
                              <TableCell align="right">
                                <TextField
                                  type="number"
                                  value={val}
                                  onChange={(e) => {
                                    const newArray = [...values.numConferencesDaily];
                                    newArray[idx] = parseInt(e.target.value) || 0;
                                    setFieldValue('numConferencesDaily', newArray);
                                  }}
                                  InputProps={{ inputProps: { min: 0, step: 1 } }}
                                  size="small"
                                  sx={{ width: '100px' }}
                                />
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Stack>
                    </Box>
                  </Grid>

                  <Grid size={{ xs: 12, md: 4 }}>
                    <Box>
                      <Typography variant="h6" gutterBottom>
                        {messages.fields.numWorkersDaily}
                      </Typography>
                  <Stack spacing={2}>
                    <Box display="flex" gap={2} alignItems="center">
                      <TextField
                        type="number"
                        label={messages.fields.fillAllWorkers}
                        value={fillWorkersValue}
                        onChange={(e) => setFillWorkersValue(e.target.value)}
                        InputProps={{ inputProps: { min: 0, step: 1 } }}
                        size="small"
                        sx={{ flex: 1 }}
                      />
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => {
                          const val = parseInt(fillWorkersValue) || 0;
                          setFieldValue('numWorkersDaily', Array(values.planningHorizonDays).fill(val));
                        }}
                        sx={{ minWidth: '100px' }}
                      >
                        Fill All
                      </Button>
                    </Box>
                    <TableContainer component={Paper}>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell><strong>Day</strong></TableCell>
                            <TableCell align="right"><strong>Workers</strong></TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {values.numWorkersDaily.map((val, idx) => (
                            <TableRow key={idx}>
                              <TableCell>Day {idx + 1}</TableCell>
                              <TableCell align="right">
                                <TextField
                                  type="number"
                                  value={val}
                                  onChange={(e) => {
                                    const newArray = [...values.numWorkersDaily];
                                    newArray[idx] = parseInt(e.target.value) || 0;
                                    setFieldValue('numWorkersDaily', newArray);
                                  }}
                                  InputProps={{ inputProps: { min: 0, step: 1 } }}
                                  size="small"
                                  sx={{ width: '100px' }}
                                />
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Stack>
                    </Box>
                  </Grid>

                  <Grid size={{ xs: 12, md: 4 }}>
                    <Box>
                      <Typography variant="h6" gutterBottom>
                        {messages.fields.purchaseCostsDaily}
                      </Typography>
                  <Stack spacing={2}>
                    <Box display="flex" gap={2} alignItems="center">
                      <TextField
                        type="number"
                        label={messages.fields.fillAllCosts}
                        value={fillCostsValue}
                        onChange={(e) => setFillCostsValue(e.target.value)}
                        InputProps={{ inputProps: { min: 0, step: 1 } }}
                        size="small"
                        sx={{ flex: 1 }}
                      />
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => {
                          const val = parseInt(fillCostsValue) || 0;
                          setFieldValue('purchaseCostsDaily', Array(values.planningHorizonDays).fill(val));
                        }}
                        sx={{ minWidth: '100px' }}
                      >
                        Fill All
                      </Button>
                    </Box>
                    <TableContainer component={Paper}>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell><strong>Day</strong></TableCell>
                            <TableCell align="right"><strong>Cost (PLN/kg)</strong></TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {values.purchaseCostsDaily.map((val, idx) => (
                            <TableRow key={idx}>
                              <TableCell>Day {idx + 1}</TableCell>
                              <TableCell align="right">
                                <TextField
                                  type="number"
                                  value={val}
                                  onChange={(e) => {
                                    const newArray = [...values.purchaseCostsDaily];
                                    newArray[idx] = parseInt(e.target.value) || 0;
                                    setFieldValue('purchaseCostsDaily', newArray);
                                  }}
                                  InputProps={{ inputProps: { min: 0, step: 1 } }}
                                  size="small"
                                  sx={{ width: '100px' }}
                                />
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Stack>
                    </Box>
                  </Grid>
                </Grid>

                <Accordion 
                  expanded={isAdvancedExpanded} 
                  onChange={() => setIsAdvancedExpanded(!isAdvancedExpanded)}
                >
                  <AccordionSummary>
                    <Typography variant="h6">
                      {isAdvancedExpanded 
                        ? messages.fields.advancedSettingsExpanded 
                        : messages.fields.advancedSettingsCollapsed}
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={2}>
                      <Grid size={{ xs: 12, md: 3 }}>
                      <Field name="storageCapacityKg">
                        {({ field, meta }: any) => (
                          <TextField
                            {...field}
                            type="number"
                            label={messages.fields.storageCapacityKg}
                            fullWidth
                            InputProps={{ inputProps: { min: 1, step: 1 } }}
                            error={meta.touched && Boolean(meta.error)}
                            helperText={meta.touched && meta.error}
                          />
                        )}
                      </Field>
                      </Grid>
                      <Grid size={{ xs: 12, md: 3 }}>
                      <Field name="transportCostPln">
                        {({ field, meta }: any) => (
                          <TextField
                            {...field}
                            type="number"
                            label={messages.fields.transportCostPln}
                            fullWidth
                            InputProps={{ inputProps: { min: 0, step: 0.01 } }}
                            error={meta.touched && Boolean(meta.error)}
                            helperText={meta.touched && meta.error}
                          />
                        )}
                      </Field>
                      </Grid>
                      <Grid size={{ xs: 12, md: 3 }}>
                      <Field name="initialInventoryKg">
                        {({ field, meta }: any) => (
                          <TextField
                            {...field}
                            type="number"
                            label={messages.fields.initialInventoryKg}
                            fullWidth
                            InputProps={{ inputProps: { min: 0, step: 0.01 } }}
                            error={meta.touched && Boolean(meta.error)}
                            helperText={meta.touched && meta.error}
                          />
                        )}
                      </Field>
                      </Grid>
                      <Grid size={{ xs: 12, md: 3 }}>
                      <Field name="dailyLossFraction">
                        {({ field, meta }: any) => (
                          <TextField
                            {...field}
                            type="number"
                            label={messages.fields.dailyLossFraction}
                            fullWidth
                            InputProps={{ inputProps: { min: 0, max: 1, step: 0.01 } }}
                            error={meta.touched && Boolean(meta.error)}
                            helperText={meta.touched && meta.error}
                          />
                        )}
                      </Field>
                      </Grid>
                    </Grid>
                  </AccordionDetails>
                </Accordion>

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
  );
};

const FormPage: React.FC<FormProps> = ({ onSubmit }) => {
  const [fillConferencesValue, setFillConferencesValue] = useState<string>('1');
  const [fillWorkersValue, setFillWorkersValue] = useState<string>('20');
  const [fillCostsValue, setFillCostsValue] = useState<string>('12');

  const handleSubmit = async (values: FormValues, { setSubmitting, resetForm }: any) => {
    try {
      if (onSubmit) {
        await onSubmit(values);
      } else {
        await submitFormData(values);
        resetForm();
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box className="form-page">
      <Formik initialValues={initialValues} validationSchema={validationSchema} onSubmit={handleSubmit}>
        {({ isSubmitting, values, setFieldValue }) => (
          <FormContent
            isSubmitting={isSubmitting}
            values={values}
            setFieldValue={setFieldValue}
            fillConferencesValue={fillConferencesValue}
            setFillConferencesValue={setFillConferencesValue}
            fillWorkersValue={fillWorkersValue}
            setFillWorkersValue={setFillWorkersValue}
            fillCostsValue={fillCostsValue}
            setFillCostsValue={setFillCostsValue}
          />
        )}
      </Formik>
    </Box>
  );
};

export default FormPage;
