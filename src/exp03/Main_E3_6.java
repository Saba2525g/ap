import java.util.Scanner;

public class Main_E3_6 {

    private int[][] matrix;
    private int rows, cols;

    public Main_E3_6() {
        Scanner input = new Scanner(System.in);

        System.out.print("Enter number of rows: ");
        rows = input.nextInt();

        System.out.print("Enter number of columns: ");
        cols = input.nextInt();

        if (rows < 2 || cols < 2) {
            System.out.println("Matrix must be at least 2x2.");
            input.close();
            return;
        }

        matrix = new int[rows][cols];

        System.out.println("Enter matrix elements:");
        fillMatrix(input);

        findAndPrintMax2x2();

        input.close();
    }

    private void fillMatrix(Scanner input) {
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                matrix[i][j] = input.nextInt();
            }
        }
    }

    private void findAndPrintMax2x2() {
        int bestSum = Integer.MIN_VALUE;
        int bestI = 0;
        int bestJ = 0;


        for (int i = 0; i <= rows - 2; i++) {
            for (int j = 0; j <= cols - 2; j++) {
                int sum =
                        matrix[i][j]     + matrix[i][j+1] +
                                matrix[i+1][j]   + matrix[i+1][j+1];

                if (sum > bestSum) {
                    bestSum = sum;
                    bestI = i;
                    bestJ = j;
                }
            }
        }

        System.out.println("Best 2x2 submatrix top left at row " + (bestI + 1) + ", column " + (bestJ + 1));
        System.out.println("Elements:");
        System.out.println(matrix[bestI][bestJ]   + " " + matrix[bestI][bestJ+1]);
        System.out.println(matrix[bestI+1][bestJ] + " " + matrix[bestI+1][bestJ+1]);
        System.out.println("Sum = " + bestSum);
    }

    public static void main(String[] args) {
        new Main_E3_6();
    }
}

