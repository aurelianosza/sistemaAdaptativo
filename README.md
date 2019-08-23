<div>

<h1>Camada Adaptativa</h1> 


<p>
Os arquivos desse repositorio, servem para a demonstração de uma camada de adaptação de sistemas baseados na arquitetura MORPH

Para executar e ver seu funcionamento segue os passos
</p>

<h3>
também precisará de previamente instalado
</h3>

<ul>
    <li>
        Docker
    </li>
    <li>
        Docker CLI
    </li>
    <li>
        docker-compose compatível com a versão 3!
    </li>
    <li>
        Python versao 3.6
    </li>
</ul>

<h3>
    Passos para rodar o servidor de simulações SWIM.
</h3>

<ul>
    <li>
        <p>
            Acesse <a href="https://github.com/aurelianosza/swim-1" target="_blank">Esse Link</a>. Faça download do repositório.
        </p>
    </li>
    <li>
        <p>
            Após o download, abra o terminal na pasta do projeto, e digite o comando       
        </p>
        <em>
            docker-compose up
        </em>
        <p>
            Se achar necessário, a documentação do repositório, mostra em bastante detalhes como fazer várias simulações no ambiente SWIM.
        </p>
    </li>
    <li>
        Após rodar o container, acesse em seu navegador de preferência o endereco <em>localhost:6901</em>,
        aparecerá um formulário pedindo uma senha para acessar o sistema no modo gráfico. A senha para acesso é <em>vncpassword</em>.
    </li>
    <li>
        Já dentro do sistema que foi aberto no navegador, siga até o diretório <em>/headless/seams-swim/swim/simulations/swim/</em>.
    </li>
    <li>
        Dentro da pasta, abra o terminal, e digite o comando <em>./run.sh Reactive 0..2</em>.
    </li>
    <li>
        Após isso, o swim estará rodando em sua maquina, mapeada na porta 4242.
    </li>
</ul>

<h3>Passos para executar a camada de comunicação com o SWIM.</h3>

<ul>
    <li>
        Faça o download desse repositório.
    </li>
    <li>
        Acesse o arquivo ini.json.
    </li>
    <li>
        No objeto <em>target</em> dentro ddo arquivo de configuração, configure o host e a porta de sua aplicação alvo. Caso esteja usando o simulador SWIM descrito acima, o arquivo esta previamente definido. 
    </li>
    <li>
        execute o arquivo de script <em>main.py</em> com o Python3.
        A saída do script são os hosts e as portas que estão configuradas para executar comandos e gerenciar eventos.
    </li>
    <li>
        acesse o servidor principal esecundario via <em>telnet</em> e execute os comandos do arquivo test.json, que lista uma sequencia de comandos. 
    </li>
    <li>
        O arquivo event.json enfatiza como fazer as operações de CRUD no servidor de eventos. Além deles, você pode verificar a lista de eventos e seus parametros no arquivo confiSwim.json
    </li>

</ul>

</div>