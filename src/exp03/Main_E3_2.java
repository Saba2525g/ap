package exp03;

import java.util.Scanner;

public class Main_E3_2 {

    private int[][] matrix = new int[2][2];           // matrix 2x2

    public Main_E3_2() {
        Scanner input = new Scanner(System.in);

        System.out.println("Enter 4 elements of 2x2 matrix:");


        for (int i = 0; i < 2; i++) {
            for (int j = 0; j < 2; j++) {
                matrix[i][j] = input.nextInt();
            }
        }


        int det = calculateDeterminant();

        System.out.println("Determinant = " + det);

        input.close();
    }

    private int calculateDeterminant() {
        int a = matrix[0][0];
        int b = matrix[0][1];
        int c = matrix[1][0];
        int d = matrix[1][1];

        return (a * d) - (b * c);
    }

    public static void main(String[] args) {
        new Main_E3_2();
    }
}

