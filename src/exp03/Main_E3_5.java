package exp03;

import java.util.Scanner;

public class Main_E3_5 {

    private int rows, cols;
    private int[][] matrix;
    private int[][] result;

    public Main_E3_5() {
        Scanner input = new Scanner(System.in);

        System.out.print("Enter number of rows: ");
        rows = input.nextInt();

        System.out.print("Enter number of columns: ");
        cols = input.nextInt();

        matrix = new int[rows][cols];

        System.out.println("Enter matrix values:");
        fillMatrix(input);

        System.out.print("Enter row index to delete (0 to " + (rows - 1) + "): ");
        int delRow = input.nextInt();

        System.out.print("Enter column index to delete (0 to " + (cols - 1) + "): ");
        int delCol = input.nextInt();

        deleteRowCol(delRow, delCol);
        printResult();

        input.close();
    }

    private void fillMatrix(Scanner input) {
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                matrix[i][j] = input.nextInt();
            }
        }
    }

    private void deleteRowCol(int delRow, int delCol) {

        result = new int[rows - 1][cols - 1];

        int newI = 0;
        for (int i = 0; i < rows; i++) {
            if (i == delRow) continue;

            int newJ = 0;
            for (int j = 0; j < cols; j++) {
                if (j == delCol) continue;

                result[newI][newJ] = matrix[i][j];
                newJ++;
            }
            newI++;
        }
    }

    private void printResult() {
        System.out.println("Matrix after deleting row & column:");
        for (int i = 0; i < result.length; i++) {
            for (int j = 0; j < result[i].length; j++) {
                System.out.print(result[i][j] + " ");
            }
            System.out.println();
        }
    }

    public static void main(String[] args) {
        new Main_E3_5();
    }
}

