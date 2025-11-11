import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Box
} from '@mui/material';
import { messages } from '../form/messages';
import './styles.scss';

export type PredictionData = {
  day: string;
  orderAmount: number;
  consumedAmount: number;
  remainingAmount: number;
  unit: string;
};

export type PredictionResultProps = {
  data: PredictionData[];
};

const PredictionResult: React.FC<PredictionResultProps> = ({ data }) => {
  return (
    <Box className="prediction-result">
      <Typography variant="h5" component="h2" gutterBottom>
        {messages.predictionResult.title}
      </Typography>
      
      <TableContainer component={Paper} className="prediction-table">
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>
                <Typography variant="subtitle2" fontWeight="bold">
                  {messages.predictionResult.headers.day}
                </Typography>
              </TableCell>
              <TableCell align="right">
                <Typography variant="subtitle2" fontWeight="bold">
                  {messages.predictionResult.headers.orderAmount}
                </Typography>
              </TableCell>
              <TableCell align="right">
                <Typography variant="subtitle2" fontWeight="bold">
                  {messages.predictionResult.headers.consumedAmount}
                </Typography>
              </TableCell>
              <TableCell align="right">
                <Typography variant="subtitle2" fontWeight="bold">
                  {messages.predictionResult.headers.remainingAmount}
                </Typography>
              </TableCell>
              <TableCell>
                <Typography variant="subtitle2" fontWeight="bold">
                  {messages.predictionResult.headers.unit}
                </Typography>
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data.map((row, index) => (
              <TableRow key={index} className="prediction-row">
                <TableCell component="th" scope="row">
                  <Typography variant="body1">
                    {row.day}
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body1" fontWeight="medium">
                    {row.orderAmount.toLocaleString()}
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body1" fontWeight="medium">
                    {row.consumedAmount.toLocaleString()}
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body1" fontWeight="medium">
                    {row.remainingAmount.toLocaleString()}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2" color="text.secondary">
                    {row.unit}
                  </Typography>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default PredictionResult;