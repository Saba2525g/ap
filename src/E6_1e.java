import java.util.Scanner; //E6.1e

public class E6_1e {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.print("Enter a number: ");
        int number = input.nextInt();

        int sum = 0;

        while (number > 0) {
            int digit = number % 10;
            if (digit % 2 != 0) {
                sum += digit;
            }
            number /= 10;
        }

        System.out.println("Sum of odd digits: " + sum);

        input.close();
    }
}

