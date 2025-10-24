import java.io.File;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Scanner;
import java.nio.file.Files;

public class Sudoku {
    public static void main(String[] args) throws Exception {
        File file = new File(Paths.get("sudoku.txt").toString());
        Scanner fileInput = new Scanner(file);

        Scanner userInput = new Scanner(System.in);

        int[][] board = new int[9][9];

        // Read Sudoku board from file
        for (int i = 0; i < 9; i++) {
            String line = fileInput.nextLine();
            for (int j = 0; j < 9; j++) {
                board[i][j] = Integer.parseInt(line.split(" ")[j]);
            }
        }
        fileInput.close();

        System.out.println("🎯 Sudoku game started! Empty cells are shown as 0.\n");

        // Main game loop
        while (!isComplete(board)) {
            // Print the board
            for (int i = 0; i < 9; i++) {
                for (int j = 0; j < 9; j++) {
                    if (board[i][j] == 0) System.out.print(". ");
                    else System.out.print(board[i][j] + " ");
                    if ((j + 1) % 3 == 0 && j != 8) System.out.print("| "); // vertical block separator
                }
                System.out.println();
                if ((i + 1) % 3 == 0 && i != 8) System.out.println("---------------------"); // horizontal block separator
            }

            // Get user input
            System.out.print("Enter row (0-8): ");
            int row = userInput.nextInt();
            System.out.print("Enter column (0-8): ");
            int col = userInput.nextInt();
            System.out.print("Enter number (1-9): ");
            int num = userInput.nextInt();

            if (board[row][col] != 0) {
                System.out.println("❌ This cell is already filled, try again.\n");
            } else if (!isValid(board, row, col, num)) {
                System.out.println("❌ This number is not allowed here (violates row, column or block rules).\n");
            } else {
                board[row][col] = num;
                System.out.println("✅ Number placed!\n");
            }
        }

        System.out.println("🎉 Congratulations! The board is complete:");
        // Print final board
        for (int i = 0; i < 9; i++) {
            for (int j = 0; j < 9; j++) {
                System.out.print(board[i][j] + " ");
            }
            System.out.println();
        }

        userInput.close();
    }

    // Check if the board is complete (no zeros left)
    public static boolean isComplete(int[][] b) {
        for (int i = 0; i < 9; i++)
            for (int j = 0; j < 9; j++)
                if (b[i][j] == 0) return false;
        return true;
    }

    // Check if placing a number is valid according to Sudoku rules
    public static boolean isValid(int[][] b, int row, int col, int num) {
        for (int i = 0; i < 9; i++)
            if (b[row][i] == num) return false; // check row
        for (int i = 0; i < 9; i++)
            if (b[i][col] == num) return false; // check column

        // check 3x3 block
        int startRow = (row / 3) * 3;
        int startCol = (col / 3) * 3;
        for (int i = startRow; i < startRow + 3; i++)
            for (int j = startCol; j < startCol + 3; j++)
                if (b[i][j] == num) return false;

        return true;
    }
}

