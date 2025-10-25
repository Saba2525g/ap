import java.util.Scanner; //E_6_2_d

public class E6_2d {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.println("Enter integers (0 to stop):");

        int oldNumber = 0;
        int newNumber = input.nextInt();

        while (newNumber != 0) {
            int nextNumber = input.nextInt();

            if (newNumber == nextNumber) {
                System.out.print(newNumber + " ");

                while (newNumber == nextNumber) {
                    newNumber = nextNumber;
                    nextNumber = input.nextInt();
                }
            }

            newNumber = nextNumber;
        }

        input.close();
    }
}

