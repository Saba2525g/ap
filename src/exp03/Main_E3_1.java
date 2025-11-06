package exp03;

import java.util.Scanner;


public class Main_E3_1 {             //this is my main class

    private int[][] A;
    private int[][] B;
    private int[][] C;

    private int r1, c1, r2, c2;


    public Main_E3_1() {

        Scanner input = new Scanner(System.in);

        System.out.print("Enter rows and columns of Matrix A: ");
        r1 = input.nextInt();
        c1 = input.nextInt();

        System.out.print("Enter rows and columns of Matrix B: ");
        r2 = input.nextInt();
        c2 = input.nextInt();


        if (c1 != r2) {                 //We will check if matrix multiplication is possible

            System.out.println("Matrix multiplication is NOT possible!");
            input.close();
            return;
        }


        A = new int[r1][c1];         //We build our matrixes here
        B = new int[r2][c2];
        C = new int[r1][c2];

        System.out.println("Enter elements of Matrix A:");
        fillMatrix(A, input);

        System.out.println("Enter elements of Matrix B:");
        fillMatrix(B, input);

        multiply();

        printResult();

        input.close();
    }

    private void fillMatrix(int[][] M, Scanner input) {
        for (int i = 0; i < M.length; i++) {
            for (int j = 0; j < M[i].length; j++) {
                M[i][j] = input.nextInt();
            }
        }
    }


    private void multiply() {
        for (int i = 0; i < r1; i++) {
            for (int j = 0; j < c2; j++) {
                int sum = 0;


                for (int k = 0; k < c1; k++) {
                    sum += A[i][k] * B[k][j];
                }


                C[i][j] = sum;
            }
        }
    }


    private void printResult() {
        System.out.println("Result Matrix (A × B):");
        for (int i = 0; i < r1; i++) {
            for (int j = 0; j < c2; j++) {
                System.out.print(C[i][j] + " ");
            }
            System.out.println();
        }
    }

    public static void main(String[] args) {
        new Main_E3_1();
    }
}
