package exp03;

import java.util.Scanner;

public class Main_E3_4 {

    private int[][] matrix;
    private int[][] transpose;
    private int rows, cols;

    public Main_E3_4() {
        Scanner input = new Scanner(System.in);

        System.out.print("Enter number of rows: ");
        rows = input.nextInt();

        System.out.print("Enter number of columns: ");
        cols = input.nextInt();

        matrix = new int[rows][cols];
        transpose = new int[cols][rows];

        System.out.println("Enter matrix elements:");
        fillMatrix(input);

        createTranspose();
        printTranspose();

        input.close();
    }

    private void fillMatrix(Scanner input) {
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                matrix[i][j] = input.nextInt();
            }
        }
    }

    private void createTranspose() {
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                transpose[j][i] = matrix[i][j];
            }
        }
    }

    private void printTranspose() {
        System.out.println("Transpose Matrix:");
        for (int i = 0; i < cols; i++) {
            for (int j = 0; j < rows; j++) {
                System.out.print(transpose[i][j] + " ");
            }
            System.out.println();
        }
    }

    public static void main(String[] args) {
        new Main_E3_4();
    }
}

