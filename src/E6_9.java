import java.util.Scanner; //E6.9

public class E6_9 {
    public static void main(String[] args) {
        Scanner input = new Scanner(System.in);

        System.out.print("Enter a word: ");
        String word = input.next();


        for (int i = word.length() - 1; i >= 0; i--) {
            char letter = word.charAt(i);
            System.out.print(letter);
        }

        input.close();
    }
}

