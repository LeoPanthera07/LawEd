"use client";

import { useState, useCallback } from "react";
import api from "@/lib/api";
import type {
  APIResponse,
  CreateOrderRequest,
  CreateOrderResponse,
  VerifyPaymentRequest,
} from "@/lib/types";

declare global {
  interface Window {
    Razorpay: new (options: Record<string, unknown>) => {
      open: () => void;
    };
  }
}

export function usePayment() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const initiatePayment = useCallback(
    async (
      data: CreateOrderRequest,
      onSuccess: (paymentId: string) => void
    ) => {
      setIsProcessing(true);
      setError(null);

      try {
        const res = await api.post<APIResponse<CreateOrderResponse>>(
          "/payments/create-order",
          data
        );
        const order = res.data.data!;

        const options = {
          key: process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID,
          amount: order.amount,
          currency: order.currency,
          name: "NyayaSetu",
          description: `Payment for ${data.payment_type}`,
          order_id: order.razorpay_order_id,
          handler: async (response: {
            razorpay_order_id: string;
            razorpay_payment_id: string;
            razorpay_signature: string;
          }) => {
            try {
              const verifyData: VerifyPaymentRequest = {
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
              };
              await api.post("/payments/verify", verifyData);
              onSuccess(response.razorpay_payment_id);
            } catch {
              setError("Payment verification failed");
            } finally {
              setIsProcessing(false);
            }
          },
          theme: { color: "#D97706" },
        };

        const rzp = new window.Razorpay(options);
        rzp.open();
      } catch (err: unknown) {
        const msg =
          (err as { response?: { data?: { error?: { message?: string } } } })
            ?.response?.data?.error?.message || "Failed to create payment";
        setError(msg);
        setIsProcessing(false);
      }
    },
    []
  );

  return { initiatePayment, isProcessing, error };
}
