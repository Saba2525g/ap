import java.util.Scanner; //E6.2c

public class E6_2c {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.println("Enter integers (0 to stop):");
        int sum = 0;
        int number = input.nextInt();

        while (number != 0) {
            sum += number;
            System.out.print(sum + " ");
            number = input.nextInt();
        }

        input.close();
    }
}

