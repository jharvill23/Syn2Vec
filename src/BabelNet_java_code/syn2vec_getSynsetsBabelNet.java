package learn.learning;

import java.io.*;
import java.util.Scanner;
import java.util.*;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonElement;
import com.google.gson.stream.JsonWriter;
import com.ibm.icu.impl.locale.LanguageTag;
import it.uniroma1.lcl.babelnet.data.*;
import it.uniroma1.lcl.babelnet.iterators.BabelIterator;
import it.uniroma1.lcl.jlt.util.UniversalPOS;
import com.google.common.collect.Multimap;

import it.uniroma1.lcl.babelnet.BabelNet;
import it.uniroma1.lcl.babelnet.BabelNetQuery;
import it.uniroma1.lcl.babelnet.BabelNetUtils;
import it.uniroma1.lcl.babelnet.BabelSense;
import it.uniroma1.lcl.babelnet.BabelSenseComparator;
import it.uniroma1.lcl.babelnet.BabelSynset;
import it.uniroma1.lcl.babelnet.BabelSynsetComparator;
import it.uniroma1.lcl.babelnet.BabelSynsetID;
import it.uniroma1.lcl.babelnet.BabelSynsetRelation;
import it.uniroma1.lcl.babelnet.InvalidSynsetIDException;
import it.uniroma1.lcl.babelnet.iterators.BabelLexiconIterator;
import it.uniroma1.lcl.babelnet.iterators.WordNetSynsetIterator;
import it.uniroma1.lcl.babelnet.iterators.BabelSynsetIterator;
import it.uniroma1.lcl.jlt.util.Language;
import it.uniroma1.lcl.jlt.util.ScoredItem;
import it.uniroma1.lcl.kb.SynsetType;
import org.apache.commons.codec.language.bm.Languages;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.search.IndexSearcher;
import it.uniroma1.lcl.jlt.ling.Word;


public class syn2vec_getSynsetsBabelNet{

    public static void mainTest()
    {
        BabelNet bn = BabelNet.getInstance();
        // First collect all .txt files to search over
        // Note: The files are named by language. For example, the list of all English query words will
        // be called 'en.txt' and the list of all Chinese query words will be called 'zh.txt' and so on for
        // other eval languages.
        // You have to populate the directory with files generated from python code
        File folder = new File("/home/john/Documents/School/Fall_2021_Projects/query_word_lists");
        File[] listOfFiles = folder.listFiles();
        Map<String, List<String>> words_by_lang = new HashMap<>();
        for (int i = 0; i < listOfFiles.length; i++) {
            try {
                String lang_name = listOfFiles[i].getName();
                lang_name = lang_name.replace(".", "@");
                String[] arrOfStr = lang_name.split("@", 2);
                lang_name = arrOfStr[0].toUpperCase();
                Scanner s = new Scanner(listOfFiles[i]);
                ArrayList<String> list = new ArrayList<String>();
                while (s.hasNextLine()){
                    list.add(s.nextLine());
                }
                s.close();
//                String word = list.get(20000);
                Language lang_object = Language.fromISO(lang_name);
                int counter = 0;
                Map<String, List<String>> word2syns = new HashMap<>();
                for (String element : list) {
                    List<BabelSynset> synsets = bn.getSynsets(element, lang_object);
                    if (synsets.size() > 0){
                        ArrayList<String> local_synsets = new ArrayList<String>();
                        for (BabelSynset local_syn : synsets){
                            String id = local_syn.getID().getID();
                            local_synsets.add(id);
//                            BabelSynset dummycheck = bn.getSynset(new BabelSynsetID(id))
                        }
                        word2syns.put(element, local_synsets);
                    }
                    if (counter % 1000 == 0){
                        System.out.println(counter);
                    }
                    counter++;
                }
                Gson gson = new GsonBuilder()
                        .setPrettyPrinting()
                        .create();
                // Depending on where you put this script, you need to create the dump directory yourself
                // We use 'word2syns_by_lang' as the dump directory
                new File("word2syns_by_lang").mkdirs();
                String lang_save_path = "word2syns_by_lang/" + lang_name + ".json";
                Writer writer = new FileWriter(lang_save_path);
                gson.toJson(word2syns, writer);
                writer.close();

            } catch (IOException e) {
                e.printStackTrace();
            }

        }

    }

    static public void main(String[] args)
    {
        try
        {
            BabelNet bn = BabelNet.getInstance();

            mainTest();

        }
        catch (Exception e)
        {
            e.printStackTrace();
        }
    }
}

