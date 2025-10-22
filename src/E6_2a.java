import java.util.Scanner; //E6.2a

public class E6_2a {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.println("Enter integers (0 to stop):");
        int number = input.nextInt();

        int min = number;
        int max = number;

        while (number != 0) {
            if (number < min) min = number;
            if (number > max) max = number;
            number = input.nextInt();
        }

        System.out.println("Smallest: " + min);
        System.out.println("Largest: " + max);

        input.close();
    }
}
